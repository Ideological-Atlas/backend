import factory
from core.factories.abstract import TimeStampedUUIDModelFactory
from core.models import Country


class CountryFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("code2",)

    name = factory.Faker("country")
    # Generamos un código de 2 letras único usando Sequence para evitar colisiones en tests
    code2 = factory.Sequence(lambda n: f"{n}"[:2].upper().zfill(2))
    flag = factory.django.ImageField(color="blue")
