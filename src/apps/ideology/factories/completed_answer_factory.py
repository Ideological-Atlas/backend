import factory
from core.factories.user_factories import VerifiedUserFactory
from ideology.models import CompletedAnswer


class CompletedAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompletedAnswer

    completed_by = factory.SubFactory(VerifiedUserFactory)
    answers = factory.LazyFunction(
        lambda: {"sample_axis_id": 0.5, "sample_conditioner": "Yes"}
    )
