from typing import Any, Optional

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
    IdeologyAxis,
    IdeologyAxisConditioner,
    IdeologyConditioner,
    IdeologyConditionerConditioner,
    IdeologySection,
    IdeologySectionConditioner,
)


class IdeologySeeder:
    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style
        self._registry: dict[str, Any] = {}
        self.complexity_level: Optional[IdeologyAbstractionComplexity] = None

    def seed(self):
        self.stdout.write("🧪 Generating Complex Test Level...")

        self.complexity_level = self._create_complexity_level()

        basic_section = self._provision_basic_section()
        self._provision_conditional_section()
        self._provision_complex_dependency_section()
        self._provision_virtual_logic_section(trigger_section=basic_section)

        self.stdout.write(self.style.SUCCESS("✅ Test Level populated successfully!"))

    def _create_complexity_level(self) -> IdeologyAbstractionComplexity:
        complexity = IdeologyAbstractionComplexityFactory(complexity=99)
        self._localize_model(
            complexity,
            name="Test Level",
            description="Debug level to validate conditional logic in the Frontend.",
        )
        return complexity

    def _provision_basic_section(self) -> IdeologySection:
        section = IdeologySectionFactory(
            abstraction_complexity=self.complexity_level, add_axes__total=0
        )
        self._localize_model(
            section,
            name="Section 1 (Basic)",
            description="No entry conditions. Contains a Trigger Axis that unlocks Section 4.",
        )
        self._create_axes_batch(section, count=10, name_prefix="S1 Question")
        return section

    def _provision_conditional_section(self):
        selector_conditioner = self._create_conditioner(
            key="cond_a",
            name="Conditioner A (Selector)",
            description="Controls visibility of Section 2. Select 'Option A' to unlock it.",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B", "Option C"],
        )

        section = IdeologySectionFactory(
            abstraction_complexity=self.complexity_level, add_axes__total=0
        )
        self._localize_model(
            section,
            name="Section 2 (Cond A)",
            description="You see this because Conditioner A is set to 'Option A'.",
        )

        self._link_condition(
            parent=section,
            conditioner=selector_conditioner,
            through_model=IdeologySectionConditioner,
            parent_field="section",
            trigger_value="Option A",
        )

        self._create_axes_batch(section, count=5, name_prefix="S2 Basic Question")
        self._provision_internal_section_logic(section)

    def _provision_internal_section_logic(self, section: IdeologySection):
        boolean_conditioner = self._create_conditioner(
            key="cond_b",
            name="Conditioner B",
            description="Controls the last 5 questions of this section. Set to 'true' to reveal them.",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )

        axes = self._create_axes_batch(section, count=5, name_prefix="S2 Cond Question")
        for axis in axes:
            self._link_condition(
                parent=axis,
                conditioner=boolean_conditioner,
                through_model=IdeologyAxisConditioner,
                parent_field="axis",
                trigger_value="true",
            )

    def _provision_complex_dependency_section(self):
        section = IdeologySectionFactory(
            abstraction_complexity=self.complexity_level, add_axes__total=0
        )
        self._localize_model(
            section,
            name="Section 3 (Complex)",
            description="You see this because C='true' AND D='true' (which required E='true').",
        )

        cond_c = self._create_conditioner(
            key="cond_c",
            name="Conditioner C",
            description="Lock 1/2 for Section 3. Set to 'true' to satisfy this part.",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )

        self._create_nested_dependency_chain_for_section(section)

        self._link_condition(
            parent=section,
            conditioner=cond_c,
            through_model=IdeologySectionConditioner,
            parent_field="section",
            trigger_value="true",
        )

        self._create_axes_batch(section, count=3, name_prefix="S3 Basic Question")
        self._provision_multi_condition_logic(section)
        self._provision_recursive_condition_logic(section)

    def _create_nested_dependency_chain_for_section(self, section: IdeologySection):
        cond_e_root = self._create_conditioner(
            key="cond_e",
            name="Conditioner E (Root)",
            description="Root dependency for Conditioner D. Set to 'true' to enable D.",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )

        cond_d_nested = self._create_conditioner(
            key="cond_d",
            name="Conditioner D (Nested)",
            description="Lock 2/2 for Section 3. Depends on E='true'. Set this to 'true' to fully unlock Section 3.",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )

        self._link_conditioners(
            target=cond_d_nested,
            source=cond_e_root,
            trigger_value="true",
            rule_name="Rule_D_needs_E",
        )

        self._link_condition(
            parent=section,
            conditioner=cond_d_nested,
            through_model=IdeologySectionConditioner,
            parent_field="section",
            trigger_value="true",
        )

    def _provision_multi_condition_logic(self, section: IdeologySection):
        cond_f = self._create_conditioner(
            key="cond_f",
            name="Conditioner F",
            description="Multi-condition Lock 1/2. Select 'Option A'.",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )
        cond_g = self._create_conditioner(
            key="cond_g",
            name="Conditioner G",
            description="Multi-condition Lock 2/2. Select 'Option A'.",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )

        axes = self._create_axes_batch(
            section, count=3, name_prefix="S3 Multi-Cond Question"
        )
        for axis in axes:
            self._link_condition(
                axis, cond_f, IdeologyAxisConditioner, "axis", "Option A"
            )
            self._link_condition(
                axis, cond_g, IdeologyAxisConditioner, "axis", "Option A"
            )

    def _provision_recursive_condition_logic(self, section: IdeologySection):
        cond_h = self._create_conditioner(
            key="cond_h",
            name="Conditioner H",
            description="Recursive Lock 1/2. Select 'Option A'.",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )

        cond_j_root = self._create_conditioner(
            key="cond_j",
            name="Conditioner J (Root)",
            description="Root dependency. Set 'true' to enable Conditioner I.",
            type=IdeologyConditioner.ConditionerType.BOOLEAN,
            accepted_values=["true", "false"],
        )

        cond_i_nested = self._create_conditioner(
            key="cond_i",
            name="Conditioner I (Nested)",
            description="Recursive Lock 2/2. Depends on J='true'. Select 'Option A' to unlock questions.",
            type=IdeologyConditioner.ConditionerType.CATEGORICAL,
            accepted_values=["Option A", "Option B"],
        )

        self._link_conditioners(
            target=cond_i_nested,
            source=cond_j_root,
            trigger_value="true",
            rule_name="Rule_I_needs_J",
        )

        axes = self._create_axes_batch(
            section, count=4, name_prefix="S3 Recursive-Multi Question"
        )
        for axis in axes:
            self._link_condition(
                axis, cond_h, IdeologyAxisConditioner, "axis", "Option A"
            )
            self._link_condition(
                axis, cond_i_nested, IdeologyAxisConditioner, "axis", "Option A"
            )

    def _provision_virtual_logic_section(self, trigger_section: IdeologySection):
        trigger_axis = trigger_section.axes.first()
        self._localize_model(
            trigger_axis,
            name="S1 Trigger Axis",
            description="If you set this value > 50, Section 4 will appear.",
        )

        virtual_cond = self._create_conditioner(
            key="cond_virtual",
            name="Virtual Cond (Triggered by S1 > 50)",
            description="Automatic: Becomes 'true' if S1 Trigger Axis is between 50 and 100.",
            type=IdeologyConditioner.ConditionerType.AXIS_RANGE,
            source_axis=trigger_axis,
            axis_min_value=50,
            axis_max_value=100,
        )

        section = IdeologySectionFactory(
            abstraction_complexity=self.complexity_level, add_axes__total=0
        )
        self._localize_model(
            section,
            name="Section 4 (Virtual Locked)",
            description="You see this because 'S1 Trigger Axis' in Section 1 is > 50.",
        )

        self._link_condition(
            section, virtual_cond, IdeologySectionConditioner, "section", "true"
        )

        self._create_axes_batch(section, count=3, name_prefix="S4 Secret Question")

    @staticmethod
    def _localize_model(obj, **kwargs):
        with translation.override("es"):
            for field, value in kwargs.items():
                setattr(obj, field, f"[TEST-ES] {value}")
        with translation.override("en"):
            for field, value in kwargs.items():
                setattr(obj, field, f"[TEST-EN] {value}")
        obj.save()

    def _create_axes_batch(self, section, count, name_prefix) -> list[IdeologyAxis]:
        axes = []
        for i in range(count):
            axis = IdeologyAxisFactory(section=section)
            self._localize_model(axis, name=f"{name_prefix} {i + 1}")
            axes.append(axis)
        return axes

    def _create_conditioner(self, key, **kwargs) -> IdeologyConditioner:
        name = kwargs.pop("name")
        description = kwargs.pop("description")
        conditioner = IdeologyConditionerFactory(**kwargs)
        self._localize_model(conditioner, name=name, description=description)
        self._registry[key] = conditioner
        return conditioner

    @staticmethod
    def _link_condition(
        parent, conditioner, through_model, parent_field, trigger_value
    ):
        through_model.objects.create(
            **{
                parent_field: parent,
                "conditioner": conditioner,
                "name": f"Rule_{parent.name[:10]}_{conditioner.name[:10]}",
                "condition_values": [trigger_value],
            }
        )

    @staticmethod
    def _link_conditioners(target, source, trigger_value, rule_name):
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=target,
            source_conditioner=source,
            name=rule_name,
            condition_values=[trigger_value],
        )


class Command(BaseCommand):
    help = "Populates the DB with a specific complex Test Level structure."

    def handle(self, *args, **options):
        if self._test_data_exists():
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Test Level (Complexity 99) already exists. Skipping population."
                )
            )
            return

        with transaction.atomic():
            seeder = IdeologySeeder(self.stdout, self.style)
            seeder.seed()

    @staticmethod
    def _test_data_exists() -> bool:
        return IdeologyAbstractionComplexity.objects.filter(complexity=99).exists()
