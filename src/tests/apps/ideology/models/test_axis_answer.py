from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import AxisAnswerFactory, IdeologyAxisFactory, IdeologyFactory


class AxisAnswerModelTestCase(TestCase):
    def test_str_representations(self):
        user = UserFactory(username="u1")
        ideo = IdeologyFactory(name="I1")
        axis = IdeologyAxisFactory(name="A1")

        ans_user = AxisAnswerFactory(user=user, ideology=None, axis=axis, value=0.5)
        ans_ideo = AxisAnswerFactory(
            trait_ideology=True, ideology=ideo, axis=axis, value=-0.5
        )

        self.assertEqual(str(ans_user), "A1: 0.5 (u1)")
        self.assertEqual(str(ans_ideo), "A1: -0.5 (I1)")
