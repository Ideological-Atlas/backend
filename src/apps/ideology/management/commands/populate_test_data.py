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
    IdeologyAbstractionComplexity,
    IdeologyAxisConditioner,
    IdeologyConditioner,
    IdeologyConditionerConditioner,
    IdeologySectionConditioner,
)


class Command(BaseCommand):
    help = "Populates the DB with a specific complex Test Level structure."

    def handle(self, *args, **options):
        if IdeologyAbstractionComplexity.objects.filter(complexity=99).exists():
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Test Level (Complexity 99) already exists. Skipping population."
                )
            )
            return

        self.stdout.write("🧪 Generating Complex Test Level...")

        with transaction.atomic():
            self._create_test_level()

        self.stdout.write(self.style.SUCCESS("✅ Test Level populated successfully!"))

    def _set_translations(self, ideology_object, **kwargs):
        with translation.override("es"):
            for field_name, field_value in kwargs.items():
                setattr(ideology_object, field_name, f"[TEST-ES] {field_value}")
        with translation.override("en"):
            for field_name, field_value in kwargs.items():
                setattr(ideology_object, field_name, f"[TEST-EN] {field_value}")
        ideology_object.save()

    def _link_condition(
        self,
        parent_object,
        ideology_conditioner,
        through_model_class,
        parent_field_name,
        trigger_value=None,
    ):
        final_trigger = (
            trigger_value if trigger_value else ideology_conditioner.accepted_values[0]
        )

        creation_arguments = {
            parent_field_name: parent_object,
            "conditioner": ideology_conditioner,
            "name": f"Rule_{parent_object.name}_{ideology_conditioner.name}",
            "condition_values": [final_trigger],
        }
        through_model_class.objects.create(**creation_arguments)

    def _create_test_level(self):
        ideology_abstraction_complexity = IdeologyAbstractionComplexityFactory(
            complexity=99
        )
        self._set_translations(
            ideology_abstraction_complexity,
            name="Test Level",
            description="Level for validation.",
        )

        ideology_section_basic = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_basic,
            name="Section 1 (Basic)",
            description="No conditions here.",
        )

        for i in range(10):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_basic)
            self._set_translations(ideology_axis, name=f"S1 Question {i + 1}")

        ideology_conditioner_selector = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B", "Option C"],
        )
        self._set_translations(
            ideology_conditioner_selector,
            name="Conditioner A (Selector)",
            description="Controls Section 2",
        )

        ideology_section_conditional = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_conditional,
            name="Section 2 (Cond A)",
            description="Visible if Cond A is Option A.",
        )
        self._link_condition(
            ideology_section_conditional,
            ideology_conditioner_selector,
            IdeologySectionConditioner,
            "section",
            trigger_value="Option A",
        )

        for i in range(5):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_conditional)
            self._set_translations(ideology_axis, name=f"S2 Basic Question {i + 1}")

        ideology_conditioner_boolean = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_boolean,
            name="Conditioner B",
            description="Controls last 5 qs of Sec 2",
        )

        for i in range(5):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_conditional)
            self._set_translations(ideology_axis, name=f"S2 Cond Question {i + 1}")
            self._link_condition(
                ideology_axis,
                ideology_conditioner_boolean,
                IdeologyAxisConditioner,
                "axis",
                trigger_value="true",
            )

        ideology_conditioner_c = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_c,
            name="Conditioner C",
            description="Part 1 of Sec 3 lock.",
        )

        ideology_conditioner_e = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_e,
            name="Conditioner E (Root)",
            description="Controls D.",
        )

        ideology_conditioner_d = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_d,
            name="Conditioner D (Nested)",
            description="Part 2 of Sec 3 lock.",
        )

        IdeologyConditionerConditioner.objects.create(
            target_conditioner=ideology_conditioner_d,
            source_conditioner=ideology_conditioner_e,
            name="Rule_D_needs_E",
            condition_values=["true"],
        )

        ideology_section_complex = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_complex,
            name="Section 3 (Complex)",
            description="Requires C and D(->E).",
        )

        self._link_condition(
            ideology_section_complex,
            ideology_conditioner_c,
            IdeologySectionConditioner,
            "section",
            trigger_value="true",
        )
        self._link_condition(
            ideology_section_complex,
            ideology_conditioner_d,
            IdeologySectionConditioner,
            "section",
            trigger_value="true",
        )

        for i in range(3):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_complex)
            self._set_translations(ideology_axis, name=f"S3 Basic Question {i + 1}")

        ideology_conditioner_f = IdeologyConditionerFactory(
            name="Conditioner F",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_f,
            name="Conditioner F",
            description="Multi condition part 1",
        )

        ideology_conditioner_g = IdeologyConditionerFactory(
            name="Conditioner G",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_g,
            name="Conditioner G",
            description="Multi condition part 2",
        )

        for i in range(3):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_complex)
            self._set_translations(
                ideology_axis, name=f"S3 Multi-Cond Question {i + 1}"
            )
            self._link_condition(
                ideology_axis,
                ideology_conditioner_f,
                IdeologyAxisConditioner,
                "axis",
                trigger_value="Option A",
            )
            self._link_condition(
                ideology_axis,
                ideology_conditioner_g,
                IdeologyAxisConditioner,
                "axis",
                trigger_value="Option A",
            )

        ideology_conditioner_h = IdeologyConditionerFactory(
            name="Conditioner H",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_h,
            name="Conditioner H",
            description="Multi recursive part 1",
        )

        ideology_conditioner_j = IdeologyConditionerFactory(
            name="Conditioner J (Root)",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_j,
            name="Conditioner J (Root)",
            description="Multi recursive root",
        )

        ideology_conditioner_i = IdeologyConditionerFactory(
            name="Conditioner I (Nested)",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_i,
            name="Conditioner I (Nested)",
            description="Multi recursive nested",
        )

        IdeologyConditionerConditioner.objects.create(
            target_conditioner=ideology_conditioner_i,
            source_conditioner=ideology_conditioner_j,
            name="Rule_I_needs_J",
            condition_values=["true"],
        )

        for i in range(4):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_complex)
            self._set_translations(
                ideology_axis, name=f"S3 Recursive-Multi Question {i + 1}"
            )
            self._link_condition(
                ideology_axis,
                ideology_conditioner_h,
                IdeologyAxisConditioner,
                "axis",
                trigger_value="Option A",
            )
            self._link_condition(
                ideology_axis,
                ideology_conditioner_i,
                IdeologyAxisConditioner,
                "axis",
                trigger_value="Option A",
            )
