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
    condition_values = factory.LazyFunction(list)
