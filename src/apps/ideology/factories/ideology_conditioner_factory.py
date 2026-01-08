import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_abstraction_complexity_factory import (
    IdeologyAbstractionComplexityFactory,
)
from ideology.models import IdeologyConditioner


class IdeologyConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditioner

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    type = IdeologyConditioner.ConditionerType.CATEGORICAL
    abstraction_complexity = factory.SubFactory(IdeologyAbstractionComplexityFactory)
    accepted_values = ["Option A", "Option B", "Option C"]
