import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.models import IdeologyConditionerConditioner


class IdeologyConditionerConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditionerConditioner

    target_conditioner = factory.SubFactory(IdeologyConditionerFactory)
    source_conditioner = factory.SubFactory(IdeologyConditionerFactory)
    name = factory.Sequence(lambda n: f"CondRule-{n}")
    description = factory.Faker("sentence")
    condition_values = factory.LazyFunction(list)
