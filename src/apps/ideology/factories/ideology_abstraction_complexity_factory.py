import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.models import IdeologyAbstractionComplexity


class IdeologyAbstractionComplexityFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyAbstractionComplexity
        django_get_or_create = ("complexity",)

    name = factory.Sequence(lambda n: f"Level-{n}")
    description = factory.Faker("sentence")
    complexity = factory.Sequence(lambda n: n + 100)
    visible = True

    @factory.post_generation
    def add_sections(self, create, extracted, **kwargs):
        if not create:
            return
        from ideology.factories.ideology_section_factory import IdeologySectionFactory

        total = kwargs.get("total", 0)
        for _ in range(total):
            IdeologySectionFactory(abstraction_complexity=self)
