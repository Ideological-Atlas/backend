from django.test import TestCase
from ideology.factories import IdeologyAbstractionComplexityFactory
from ideology.models import IdeologyAbstractionComplexity


class IdeologyAbstractionComplexityManagerTestCase(TestCase):
    def test_managers_properties(self):
        visible = IdeologyAbstractionComplexityFactory(visible=True)
        hidden = IdeologyAbstractionComplexityFactory(visible=False)

        visible_qs = IdeologyAbstractionComplexity.objects.visible
        self.assertIn(visible, visible_qs)
        self.assertNotIn(hidden, visible_qs)

        hidden_qs = IdeologyAbstractionComplexity.objects.not_visible
        self.assertIn(hidden, hidden_qs)
        self.assertNotIn(visible, hidden_qs)
