import factory
from cities_light.models import Region
from core.factories.country_factories import CountryFactory
from django.utils.text import slugify


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region
        django_get_or_create = ("name", "country")

    name = factory.Faker("state")
    country = factory.SubFactory(CountryFactory)
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
