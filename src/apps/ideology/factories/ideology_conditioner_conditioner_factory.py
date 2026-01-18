import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.models import IdeologyConditionerConditioner


class IdeologyConditionerConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditionerConditioner

    target_conditioner = factory.SubFactory(IdeologyConditionerFactory)
    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    name = factory.Sequence(lambda n: f"CondRule-{n}")
    description = factory.Faker("sentence")

    @factory.lazy_attribute
    def condition_values(self):
        if self.conditioner and self.conditioner.accepted_values:
            return [self.conditioner.accepted_values[0]]
        return ["true"]
