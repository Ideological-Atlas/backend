import factory
from django.utils import timezone


class TimeStampedUUIDModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    created = factory.LazyFunction(timezone.now)
    modified = factory.LazyFunction(timezone.now)
