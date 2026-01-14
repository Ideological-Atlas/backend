from django.db.utils import IntegrityError
from django.test import TestCase
from ideology.factories import (
    IdeologyAssociationFactory,
    IdeologyFactory,
    ReligionFactory,
)


class IdeologyAssociationModelTestCase(TestCase):
    def test_str_permutations(self):
        ideo = IdeologyFactory(name="Ideology")
        rel = ReligionFactory(name="Rel")
        assoc1 = IdeologyAssociationFactory(
            ideology=ideo, country__name="Spain", religion=rel, region=None
        )
        s1 = str(assoc1)
        self.assertIn("Ideology", s1)
        self.assertIn("in Spain", s1)
        self.assertIn("linked to Rel", s1)
        self.assertNotIn("(", s1)
        assoc2 = IdeologyAssociationFactory(
            ideology=ideo, country__name="Spain", religion=None, region=None
        )
        s2 = str(assoc2)
        self.assertIn("in Spain", s2)
        self.assertNotIn("linked to", s2)
        assoc3 = IdeologyAssociationFactory(
            ideology=ideo, trait_religion=True, religion=rel
        )
        s3 = str(assoc3)
        self.assertIn("linked to Rel", s3)
        self.assertNotIn("in ", s3)
        assoc4 = IdeologyAssociationFactory(
            ideology=ideo, trait_region=True, region__name="Cat"
        )
        s4 = str(assoc4)
        self.assertIn("(Cat)", s4)
        self.assertNotIn("in ", s4)
        assoc5 = IdeologyAssociationFactory.build(
            ideology=ideo, country=None, region=None, religion=None
        )
        self.assertEqual(str(assoc5), "Ideology")

    def test_constraint_requires_context(self):
        with self.assertRaises(IntegrityError):
            IdeologyAssociationFactory(country=None, region=None, religion=None)
