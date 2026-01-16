import random

import factory
from core.factories import TimeStampedUUIDModelFactory, add_related_conditioners
from ideology.factories.ideology_abstraction_complexity_factory import (
    IdeologyAbstractionComplexityFactory,
)
from ideology.models import IdeologySection, IdeologySectionConditioner


class IdeologySectionFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologySection

    name = factory.Faker("word")
    description = factory.Faker("paragraph")
    abstraction_complexity = factory.SubFactory(IdeologyAbstractionComplexityFactory)

    @factory.post_generation
    def add_axes(self, create, extracted, **kwargs):
        if not create:
            return
        from ideology.factories.ideology_axis_factory import IdeologyAxisFactory

        min_count = kwargs.get("min", 0)
        max_count = kwargs.get("max", 3)
        total = kwargs.get("total", None)
        if total is not None:
            count = total
        else:
            count = random.randint(min_count, max_count)
        for _ in range(count):
            IdeologyAxisFactory(section=self)

    @factory.post_generation
    def add_conditioners(self, create, extracted, **kwargs):
        add_related_conditioners(
            obj=self,
            create=create,
            extracted=extracted,
            through_model=IdeologySectionConditioner,
            parent_field="section",
            name_prefix="SectionRule",
            **kwargs,
        )
