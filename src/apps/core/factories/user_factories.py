import uuid

from core.factories import TimeStampedUUIDModelFactory
from django.contrib.auth import get_user_model
from factory import Faker, LazyFunction, PostGenerationMethodCall
from factory.fuzzy import FuzzyText


class UserFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("email", "username")

    password = PostGenerationMethodCall("set_password", "adm1n")
    username = Faker("email")
    email = Faker("email")
    bio = FuzzyText()
    first_name = FuzzyText(length=10)
    last_name = FuzzyText(length=10)
    is_staff = False
    is_active = True
    is_superuser = False
    is_verified = False
    verification_uuid = LazyFunction(uuid.uuid4)


class VerifiedUserFactory(UserFactory):
    is_verified = True
    verification_uuid = None
