from django.contrib.auth import get_user_model
from factory import Faker, PostGenerationMethodCall
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ("email", "username")

    password = PostGenerationMethodCall("set_password", "adm1n")
    username = Faker("email")
    email = Faker("email")
    first_name = FuzzyText(length=10)
    last_name = FuzzyText(length=10)
    is_staff = False
    is_active = True
    is_superuser = False
    is_verified = False


class VerifiedUserFactory(UserFactory):
    is_verified = True
