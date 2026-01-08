import factory
from core.factories import TimeStampedUUIDModelFactory
from core.factories.user_factories import VerifiedUserFactory
from ideology.factories.ideology_conditioner_factory import IdeologyConditionerFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.models import ConditionerAnswer


class ConditionerAnswerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = ConditionerAnswer

    conditioner = factory.SubFactory(IdeologyConditionerFactory)
    answer = "Option A"

    user = factory.SubFactory(VerifiedUserFactory)
    ideology = None

    class Params:
        trait_ideology = factory.Trait(
            user=None, ideology=factory.SubFactory(IdeologyFactory)
        )
