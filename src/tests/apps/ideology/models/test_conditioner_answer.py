from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    ConditionerAnswerFactory,
    IdeologyConditionerFactory,
    IdeologyFactory,
)


class ConditionerAnswerModelTestCase(TestCase):
    def test_str_representations(self):
        user = UserFactory(username="u1")
        ideo = IdeologyFactory(name="I1")
        cond = IdeologyConditionerFactory(name="C1")

        ans_user = ConditionerAnswerFactory(
            user=user, ideology=None, conditioner=cond, answer="Y"
        )
        ans_ideo = ConditionerAnswerFactory(
            trait_ideology=True, ideology=ideo, conditioner=cond, answer="N"
        )

        self.assertEqual(str(ans_user), "C1: Y (u1)")
        self.assertEqual(str(ans_ideo), "C1: N (I1)")
