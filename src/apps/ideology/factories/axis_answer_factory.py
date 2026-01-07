import random

import factory
from core.factories import TimeStampedUUIDModelFactory
from core.factories.user_factories import VerifiedUserFactory
from ideology.factories.ideology_axis_factory import IdeologyAxisFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.models import AxisAnswer


class AxisAnswerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = AxisAnswer

    axis = factory.SubFactory(IdeologyAxisFactory)
    value = factory.LazyFunction(lambda: round(random.uniform(-1.0, 1.0), 4))  # nosec
    margin_left = 0.1
    margin_right = 0.1

    user = factory.SubFactory(VerifiedUserFactory)
    ideology = None

    class Params:
        trait_ideology = factory.Trait(
            user=None, ideology=factory.SubFactory(IdeologyFactory)
        )
