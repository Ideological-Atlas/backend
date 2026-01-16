import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_axis_factory import IdeologyAxisFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.models import IdeologyAxisConditioner


class IdeologyAxisConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyAxisConditioner

    axis = factory.SubFactory(IdeologyAxisFactory)
    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    name = factory.Sequence(lambda n: f"AxisRule-{n}")
    description = factory.Faker("sentence")

    @factory.lazy_attribute
    def condition_values(self):
        if self.conditioner and self.conditioner.accepted_values:
            return [self.conditioner.accepted_values[0]]
        return ["true"]
