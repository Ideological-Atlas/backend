import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.models import IdeologyConditioner


class IdeologyConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditioner

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    type = IdeologyConditioner.ConditionerType.CATEGORICAL
    accepted_values = ["Option A", "Option B", "Option C"]
