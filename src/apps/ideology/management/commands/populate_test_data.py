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
                setattr(ideology_object, field_name, field_value)
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
            description="Debug level to validate conditional logic in the Frontend.",
        )

        ideology_section_basic = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_basic,
            name="Section 1 (Basic)",
            description="No entry conditions. Contains a Trigger Axis that unlocks Section 4.",
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
            description="Controls visibility of Section 2. Select 'Option A' to unlock it.",
        )

        ideology_section_conditional = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_conditional,
            name="Section 2 (Cond A)",
            description="You see this because Conditioner A is set to 'Option A'.",
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
            description="Controls the last 5 questions of this section. Set to 'true' to reveal them.",
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
            description="Lock 1/2 for Section 3. Set to 'true' to satisfy this part.",
        )

        ideology_conditioner_e = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_e,
            name="Conditioner E (Root)",
            description="Root dependency for Conditioner D. Set to 'true' to enable D.",
        )

        ideology_conditioner_d = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_d,
            name="Conditioner D (Nested)",
            description="Lock 2/2 for Section 3. Depends on E='true'. Set this to 'true' to fully unlock Section 3.",
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
            description="You see this because C='true' AND D='true' (which required E='true').",
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
            description="Multi-condition Lock 1/2. Select 'Option A'.",
        )

        ideology_conditioner_g = IdeologyConditionerFactory(
            name="Conditioner G",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_g,
            name="Conditioner G",
            description="Multi-condition Lock 2/2. Select 'Option A'.",
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
            description="Recursive Lock 1/2. Select 'Option A'.",
        )

        ideology_conditioner_j = IdeologyConditionerFactory(
            name="Conditioner J (Root)",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )
        self._set_translations(
            ideology_conditioner_j,
            name="Conditioner J (Root)",
            description="Root dependency. Set 'true' to enable Conditioner I.",
        )

        ideology_conditioner_i = IdeologyConditionerFactory(
            name="Conditioner I (Nested)",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        self._set_translations(
            ideology_conditioner_i,
            name="Conditioner I (Nested)",
            description="Recursive Lock 2/2. Depends on J='true'. Select 'Option A' to unlock questions.",
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

        trigger_axis = ideology_section_basic.axes.first()
        self._set_translations(
            trigger_axis,
            name="S1 Trigger Axis",
            description="If you set this value > 50, Section 4 will appear.",
        )

        ideology_conditioner_virtual = IdeologyConditionerFactory(
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=trigger_axis,
            axis_min_value=50,
            axis_max_value=100,
        )
        self._set_translations(
            ideology_conditioner_virtual,
            name="Virtual Cond (Triggered by S1 > 50)",
            description="Automatic: Becomes 'true' if S1 Trigger Axis is between 50 and 100.",
        )

        ideology_section_virtual = IdeologySectionFactory(
            abstraction_complexity=ideology_abstraction_complexity, add_axes__total=0
        )
        self._set_translations(
            ideology_section_virtual,
            name="Section 4 (Virtual Locked)",
            description="You see this because 'S1 Trigger Axis' in Section 1 is > 50.",
        )

        self._link_condition(
            ideology_section_virtual,
            ideology_conditioner_virtual,
            IdeologySectionConditioner,
            "section",
            trigger_value="true",
        )

        for i in range(3):
            ideology_axis = IdeologyAxisFactory(section=ideology_section_virtual)
            self._set_translations(ideology_axis, name=f"S4 Secret Question {i + 1}")
