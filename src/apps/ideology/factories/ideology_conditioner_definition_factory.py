import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.models import IdeologyConditionerDefinition


class IdeologyConditionerDefinitionFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditionerDefinition

    ideology = factory.SubFactory(IdeologyFactory)
    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    answer = "Option A"
