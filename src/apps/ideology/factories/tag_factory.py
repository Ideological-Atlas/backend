import factory
from ideology.models import Tag


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Tag-{n}")
    description = factory.Faker("sentence")
