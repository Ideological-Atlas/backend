import factory
from core.factories import TimeStampedUUIDModelFactory
from ideology.models import Religion


class ReligionFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = Religion
        django_get_or_create = ("name",)

    name = factory.Faker("word")
    description = factory.Faker("sentence")
