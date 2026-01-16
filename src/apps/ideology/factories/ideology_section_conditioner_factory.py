import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.factories.ideology_section_factory import IdeologySectionFactory
from ideology.models import IdeologySectionConditioner


class IdeologySectionConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologySectionConditioner

    section = factory.SubFactory(IdeologySectionFactory)
    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    name = factory.Sequence(lambda n: f"SectionRule-{n}")
    description = factory.Faker("sentence")

    @factory.lazy_attribute
    def condition_values(self):
        if self.conditioner and self.conditioner.accepted_values:
            return [self.conditioner.accepted_values[0]]
        return ["true"]
