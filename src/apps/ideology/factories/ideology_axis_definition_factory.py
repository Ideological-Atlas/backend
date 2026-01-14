import random

import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_axis_factory import IdeologyAxisFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.models import IdeologyAxisDefinition


class IdeologyAxisDefinitionFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyAxisDefinition

    ideology = factory.SubFactory(IdeologyFactory)
    axis = factory.SubFactory(IdeologyAxisFactory)
    value = factory.LazyFunction(lambda: random.randint(-100, 100))
    margin_left = 0
    margin_right = 0
    is_indifferent = False
