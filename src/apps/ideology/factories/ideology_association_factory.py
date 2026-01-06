import factory
from core.factories.country_factories import CountryFactory
from core.factories.region_factories import RegionFactory
from ideology.factories.ideology_factory import IdeologyFactory
from ideology.factories.religion_factory import ReligionFactory
from ideology.models import IdeologyAssociation


class IdeologyAssociationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IdeologyAssociation

    ideology = factory.SubFactory(IdeologyFactory)

    country = factory.SubFactory(CountryFactory)
    region = None
    religion = None

    class Params:
        trait_region = factory.Trait(
            country=None, religion=None, region=factory.SubFactory(RegionFactory)
        )

        trait_religion = factory.Trait(
            country=None, region=None, religion=factory.SubFactory(ReligionFactory)
        )
