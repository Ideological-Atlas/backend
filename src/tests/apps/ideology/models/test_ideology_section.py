from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)


class IdeologySectionModelTestCase(TestCase):
    def test_str_representations(self):
        abs_comp = IdeologyAbstractionComplexityFactory(name="Basic")
        cond = IdeologyConditionerFactory(name="Cond")

        sec1 = IdeologySectionFactory(
            name="Eco", abstraction_complexity=abs_comp, conditioned_by=None
        )
        self.assertEqual(str(sec1), "Eco (Basic)")

        sec2 = IdeologySectionFactory(
            name="Soc",
            abstraction_complexity=abs_comp,
            conditioned_by=cond,
            condition_values=["Value A"],
        )
        self.assertEqual(str(sec2), f"Soc (Basic) [If {cond.name} IN ['Value A']]")
