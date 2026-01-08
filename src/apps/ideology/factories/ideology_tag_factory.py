import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.factories.tag_factory import TagFactory
from ideology.models import IdeologyTag


class IdeologyTagFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyTag

    ideology = factory.SubFactory(IdeologyFactory)
    tag = factory.SubFactory(TagFactory)
