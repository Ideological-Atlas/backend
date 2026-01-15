from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import translation
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import (
    IdeologyAxisConditioner,
    IdeologyConditioner,
    IdeologyConditionerConditioner,
    IdeologySectionConditioner,
)


class Command(BaseCommand):
    help = "Populates the DB with a specific complex Test Level structure."

    def handle(self, *args, **options):
        self.stdout.write("🧪 Generating Complex Test Level...")

        with transaction.atomic():
            self._create_test_level()

        self.stdout.write(self.style.SUCCESS("✅ Test Level populated successfully!"))

    @staticmethod
    def _set_trans(obj, **kwargs):
        with translation.override("es"):
            for f, v in kwargs.items():
                setattr(obj, f, f"[TEST-ES] {v}")
        with translation.override("en"):
            for f, v in kwargs.items():
                setattr(obj, f, f"[TEST-EN] {v}")
        obj.save()

    @staticmethod
    def _link_condition(parent, conditioner, model_class, parent_field):
        # Pick the first valid value to trigger the condition
        trigger_value = conditioner.accepted_values[0]

        kwargs = {
            parent_field: parent,
            "conditioner": conditioner,
            "name": f"Rule_{parent.name}_{conditioner.name}",
            "condition_values": [trigger_value],
        }
        model_class.objects.create(**kwargs)

    def _create_test_level(self):
        # 0. Create Complexity
        comp = IdeologyAbstractionComplexityFactory(complexity=99)
        self._set_trans(comp, name="Test Level", description="Level for validation.")

        # =========================================================================
        # SECTION 1: No conditional, 10 questions
        # =========================================================================
        sec_1 = IdeologySectionFactory(abstraction_complexity=comp, add_axes__total=0)
        self._set_trans(
            sec_1, name="Section 1 (Basic)", description="No conditions here."
        )

        for i in range(10):
            axis = IdeologyAxisFactory(section=sec_1)
            self._set_trans(axis, name=f"S1 Question {i+1}")

        # =========================================================================
        # SECTION 2: Conditional (Selector)
        # - 5 unconditional questions
        # - 5 conditional questions (depend on a 2nd conditioner)
        # =========================================================================

        # Conditioner A (Selector/Categorical)
        cond_a = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B", "Option C"],
        )
        self._set_trans(
            cond_a, name="Conditioner A (Selector)", description="Controls Section 2"
        )

        sec_2 = IdeologySectionFactory(abstraction_complexity=comp, add_axes__total=0)
        self._set_trans(
            sec_2,
            name="Section 2 (Cond A)",
            description="Visible if Cond A is Option A.",
        )
        self._link_condition(sec_2, cond_a, IdeologySectionConditioner, "section")

        # 5 Unconditional Axes
        for i in range(5):
            axis = IdeologyAxisFactory(section=sec_2)
            self._set_trans(axis, name=f"S2 Basic Question {i+1}")

        # Conditioner B
        cond_b = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN
        )
        self._set_trans(
            cond_b, name="Conditioner B", description="Controls last 5 qs of Sec 2"
        )

        # 5 Conditional Axes
        for i in range(5):
            axis = IdeologyAxisFactory(section=sec_2)
            self._set_trans(axis, name=f"S2 Cond Question {i+1}")
            self._link_condition(axis, cond_b, IdeologyAxisConditioner, "axis")

        # =========================================================================
        # SECTION 3: Conditional (2 Conditions: C and D)
        # - C is normal.
        # - D is conditional on E.
        # Structure:
        #   - 3 Unconditional
        #   - 3 Conditional on 2 conditions (F and G)
        #   - 4 Conditional on 2 conditions (H and I), where I depends on J.
        # =========================================================================

        # Prep Conditions for Section 3
        cond_c = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN
        )
        self._set_trans(
            cond_c, name="Conditioner C", description="Part 1 of Sec 3 lock."
        )

        cond_e = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN
        )
        self._set_trans(cond_e, name="Conditioner E (Root)", description="Controls D.")

        cond_d = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN
        )
        self._set_trans(
            cond_d, name="Conditioner D (Nested)", description="Part 2 of Sec 3 lock."
        )

        # Link D -> depends on E
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=cond_d,
            source_conditioner=cond_e,
            name="Rule_D_needs_E",
            condition_values=[cond_e.accepted_values[0]],
        )

        # Create Section 3
        sec_3 = IdeologySectionFactory(abstraction_complexity=comp, add_axes__total=0)
        self._set_trans(
            sec_3, name="Section 3 (Complex)", description="Requires C and D(->E)."
        )

        # Link Section 3 to C AND D
        self._link_condition(sec_3, cond_c, IdeologySectionConditioner, "section")
        self._link_condition(sec_3, cond_d, IdeologySectionConditioner, "section")

        # --- S3 Group 1: 3 Unconditional Axes ---
        for i in range(3):
            axis = IdeologyAxisFactory(section=sec_3)
            self._set_trans(axis, name=f"S3 Basic Question {i+1}")

        # --- S3 Group 2: 3 Axes Conditional on F AND G ---
        cond_f = IdeologyConditionerFactory(name="Conditioner F")
        cond_g = IdeologyConditionerFactory(name="Conditioner G")

        for i in range(3):
            axis = IdeologyAxisFactory(section=sec_3)
            self._set_trans(axis, name=f"S3 Multi-Cond Question {i+1}")
            self._link_condition(axis, cond_f, IdeologyAxisConditioner, "axis")
            self._link_condition(axis, cond_g, IdeologyAxisConditioner, "axis")

        # --- S3 Group 3: 4 Axes Conditional on H AND I (I->J) ---
        cond_h = IdeologyConditionerFactory(name="Conditioner H")

        cond_j = IdeologyConditionerFactory(name="Conditioner J (Root)")
        cond_i = IdeologyConditionerFactory(name="Conditioner I (Nested)")

        # Link I -> depends on J
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=cond_i,
            source_conditioner=cond_j,
            name="Rule_I_needs_J",
            condition_values=[cond_j.accepted_values[0]],
        )

        for i in range(4):
            axis = IdeologyAxisFactory(section=sec_3)
            self._set_trans(axis, name=f"S3 Recursive-Multi Question {i+1}")
            self._link_condition(axis, cond_h, IdeologyAxisConditioner, "axis")
            self._link_condition(axis, cond_i, IdeologyAxisConditioner, "axis")
