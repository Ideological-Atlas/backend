import random

import factory
from core.factories import TimeStampedUUIDModelFactory
from core.factories.user_factories import VerifiedUserFactory
from ideology.factories.ideology_axis_factory import IdeologyAxisFactory
from ideology.models import UserAxisAnswer


class UserAxisAnswerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = UserAxisAnswer

    axis = factory.SubFactory(IdeologyAxisFactory)
    value = factory.LazyFunction(lambda: random.randint(-90, 90))
    margin_left = 10
    margin_right = 10
    user = factory.SubFactory(VerifiedUserFactory)
