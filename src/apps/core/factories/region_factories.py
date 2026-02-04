import factory
from core.factories.abstract import TimeStampedUUIDModelFactory
from core.factories.country_factories import CountryFactory
from core.models import Region


class RegionFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ("name", "country")

    name = factory.Faker("state")
    country = factory.SubFactory(CountryFactory)
    flag = factory.django.ImageField(color="red")
