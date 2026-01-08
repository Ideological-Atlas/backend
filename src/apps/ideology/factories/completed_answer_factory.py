import factory
from core.factories import TimeStampedUUIDModelFactory
from core.factories.user_factories import VerifiedUserFactory
from ideology.models import CompletedAnswer


class CompletedAnswerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = CompletedAnswer

    completed_by = factory.SubFactory(VerifiedUserFactory)
    answers = factory.LazyFunction(
        lambda: [
            {"level": "Basic", "complexity": 1, "sections": [], "conditioners": []}
        ]
    )
