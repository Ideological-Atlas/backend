import factory
from core.factories import TimeStampedUUIDModelFactory
from core.factories.user_factories import VerifiedUserFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.models import UserConditionerAnswer


class UserConditionerAnswerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = UserConditionerAnswer

    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    answer = "Option A"
    user = factory.SubFactory(VerifiedUserFactory)
