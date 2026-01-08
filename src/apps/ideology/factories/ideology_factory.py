import random

import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.models import Ideology


class IdeologyFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = Ideology
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    description_supporter = factory.Faker("paragraph")
    description_detractor = factory.Faker("paragraph")
    description_neutral = factory.Faker("paragraph")
    color = factory.Faker("hex_color")

    @factory.post_generation
    def add_tags(self, create, extracted, **kwargs):
        if not create:
            return

        from ideology.factories.ideology_tag_factory import IdeologyTagFactory
        from ideology.factories.tag_factory import TagFactory

        if extracted:
            for tag in extracted:
                IdeologyTagFactory(ideology=self, tag=tag)
            return

        min_count = kwargs.get("min", 0)
        max_count = kwargs.get("max", 3)
        total = kwargs.get("total", None)

        if total is not None:
            count = total
        else:
            count = random.randint(min_count, max_count)  # nosec

        for _ in range(count):
            IdeologyTagFactory(ideology=self, tag=TagFactory())

    @factory.post_generation
    def add_associations(self, create, extracted, **kwargs):
        if not create:
            return

        from ideology.factories.ideology_association_factory import (
            IdeologyAssociationFactory,
        )

        if extracted:
            return

        min_count = kwargs.get("min", 0)
        max_count = kwargs.get("max", 2)
        total = kwargs.get("total", None)

        if total is not None:
            count = total
        else:
            count = random.randint(min_count, max_count)  # nosec

        for _ in range(count):
            IdeologyAssociationFactory(ideology=self)
