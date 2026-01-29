import random

import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.models import IdeologyAbstractionComplexity


class IdeologyAbstractionComplexityFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyAbstractionComplexity
        django_get_or_create = ("complexity",)

    name = factory.Faker("word")
    description = factory.Faker("sentence")
    complexity = factory.Sequence(lambda n: n + 1)
    visible = True

    @factory.post_generation
    def add_sections(self, create, extracted, **kwargs):
        if not create:
            return
        from ideology.factories.ideology_section_factory import IdeologySectionFactory

        min_count = kwargs.get("min", 0)
        max_count = kwargs.get("max", 2)
        total = kwargs.get("total", None)
        if total is not None:
            count = total
        else:
            count = random.randint(min_count, max_count)
        for _ in range(count):
            IdeologySectionFactory(abstraction_complexity=self)
