import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.models import IdeologyReference


class IdeologyReferenceFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyReference

    ideology = factory.SubFactory(IdeologyFactory)
    name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    url = factory.Faker("url")
