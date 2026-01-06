import string

import factory
from cities_light.models import Country
from django.utils.text import slugify


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("code2",)

    name = factory.Sequence(lambda n: f"Country {n}")

    code2 = factory.Sequence(
        lambda n: (
            string.ascii_uppercase[n // 26 % 26] + string.ascii_uppercase[n % 26]
        )
    )

    code3 = factory.Sequence(
        lambda n: (
            string.ascii_uppercase[n // 676 % 26]
            + string.ascii_uppercase[n // 26 % 26]
            + string.ascii_uppercase[n % 26]
        )
    )

    continent = "EU"
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
