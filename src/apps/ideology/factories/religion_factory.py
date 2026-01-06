import factory
from ideology.models import Religion


class ReligionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Religion
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    description = factory.Faker("sentence")
