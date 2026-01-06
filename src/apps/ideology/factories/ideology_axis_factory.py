import factory
from ideology.factories.ideology_section_factory import IdeologySectionFactory
from ideology.models import IdeologyAxis


class IdeologyAxisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IdeologyAxis

    section = factory.SubFactory(IdeologySectionFactory)
    name = factory.Sequence(lambda n: f"Axis-{n}")
    description = factory.Faker("sentence")
    left_label = "Left"
    right_label = "Right"
    conditioned_by = None
