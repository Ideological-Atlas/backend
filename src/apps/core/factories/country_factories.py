import factory
from core.factories.abstract import TimeStampedUUIDModelFactory
from core.models import Country


class CountryFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Country {n}")
    code2 = factory.Sequence(lambda n: f"{n:02}"[-2:])
    flag = factory.django.ImageField(color="blue")
