from unittest.mock import patch

from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
    UserAxisAnswerFactory,
    UserConditionerAnswerFactory,
)
from ideology.models import IdeologyAxisConditioner, IdeologySectionConditioner
from ideology.services import AnswerService


class AnswerServiceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_conditioner_map_and_enrichment_flow(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1, name="C1")
        section = IdeologySectionFactory(
            abstraction_complexity=complexity, add_axes__total=0
        )
        axis = IdeologyAxisFactory(section=section)

        cond_section = IdeologyConditionerFactory(name="CondSection")
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=cond_section, name="R1"
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=cond_section, answer="Yes"
        )

        cond_axis = IdeologyConditionerFactory(name="CondAxis")
        IdeologyAxisConditioner.objects.create(
            axis=axis, conditioner=cond_axis, name="R2"
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=cond_axis, answer="Maybe"
        )

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers[0]

        self.assertEqual(len(data["conditioners"]), 2)
        names = sorted([c["name"] for c in data["conditioners"]])
        self.assertEqual(names, ["CondAxis", "CondSection"])

    @patch("ideology.services.answer_service.IdeologyAbstractionComplexity.objects.all")
    def test_orphaned_answers_ignored(self, mock_complexities):
        comp_visible = IdeologyAbstractionComplexityFactory(complexity=1)
        comp_hidden = IdeologyAbstractionComplexityFactory(complexity=99)

        IdeologySectionFactory(abstraction_complexity=comp_visible)
        section_hidden = IdeologySectionFactory(abstraction_complexity=comp_hidden)

        axis_hidden = IdeologyAxisFactory(section=section_hidden)

        UserAxisAnswerFactory(user=self.user, axis=axis_hidden)

        cond_hidden = IdeologyConditionerFactory()
        IdeologySectionConditioner.objects.create(
            section=section_hidden, conditioner=cond_hidden, name="HiddenRule"
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=cond_hidden, answer="Hidden"
        )

        mock_complexities.return_value.order_by.return_value = [comp_visible]

        completed = AnswerService.generate_snapshot(self.user)

        self.assertEqual(len(completed.answers), 1)
        self.assertEqual(len(completed.answers[0]["conditioners"]), 0)
        self.assertEqual(len(completed.answers[0]["sections"]), 0)

    def test_multiple_axes_same_section(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1)
        section = IdeologySectionFactory(
            abstraction_complexity=complexity, name="Economia"
        )

        axis_1 = IdeologyAxisFactory(section=section, name="Mercado")
        axis_2 = IdeologyAxisFactory(section=section, name="Regulacion")

        UserAxisAnswerFactory(user=self.user, axis=axis_1, value=10)
        UserAxisAnswerFactory(user=self.user, axis=axis_2, value=-10)

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers[0]

        self.assertEqual(len(data["sections"]), 1)
        axes_list = data["sections"][0]["axes"]
        self.assertEqual(len(axes_list), 2)

        names = sorted([a["name"] for a in axes_list])
        self.assertEqual(names, ["Mercado", "Regulacion"])
