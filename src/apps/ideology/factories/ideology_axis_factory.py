import factory
from core.factories import TimeStampedUUIDModelFactory, add_related_conditioners
from ideology.factories.ideology_section_factory import IdeologySectionFactory
from ideology.models import IdeologyAxis, IdeologyAxisConditioner


class IdeologyAxisFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyAxis

    section = factory.SubFactory(IdeologySectionFactory)
    name = factory.Sequence(lambda n: f"Axis-{n}")
    description = factory.Faker("sentence")
    left_label = "Left"
    right_label = "Right"

    @factory.post_generation
    def add_conditioners(self, create, extracted, **kwargs):
        add_related_conditioners(
            obj=self,
            create=create,
            extracted=extracted,
            through_model=IdeologyAxisConditioner,
            parent_field="axis",
            name_prefix="AxisRule",
            **kwargs,
        )
