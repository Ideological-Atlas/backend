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

    def test_generate_snapshot_happy_path(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1, name="Level-1")
        section = IdeologySectionFactory(
            abstraction_complexity=complexity,
            name="Sec-1",
            add_axes__total=0,
        )
        axis = IdeologyAxisFactory(section=section, name="Axis-1")
        UserAxisAnswerFactory(user=self.user, axis=axis, value=50)

        cond = IdeologyConditionerFactory(name="Cond-1")
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=cond, name="Rule-1"
        )
        UserConditionerAnswerFactory(user=self.user, conditioner=cond, answer="Yes")

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers

        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]["sections"]), 1)
        self.assertEqual(len(data[0]["conditioners"]), 1)

    @patch("ideology.services.answer_service.IdeologyAbstractionComplexity.objects.all")
    def test_orphaned_answers_ignored(self, mock_complexities):
        comp_visible = IdeologyAbstractionComplexityFactory(complexity=1)
        sec_visible = IdeologySectionFactory(
            abstraction_complexity=comp_visible, add_axes__total=0
        )
        axis_visible = IdeologyAxisFactory(section=sec_visible)
        UserAxisAnswerFactory(user=self.user, axis=axis_visible)

        comp_hidden = IdeologyAbstractionComplexityFactory(complexity=2)
        sec_hidden = IdeologySectionFactory(
            abstraction_complexity=comp_hidden, add_axes__total=0
        )
        axis_hidden = IdeologyAxisFactory(section=sec_hidden)
        UserAxisAnswerFactory(user=self.user, axis=axis_hidden)

        cond_hidden = IdeologyConditionerFactory()
        IdeologySectionConditioner.objects.create(
            section=sec_hidden, conditioner=cond_hidden, name="HiddenRule"
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=cond_hidden, answer="Hidden"
        )

        mock_complexities.return_value.order_by.return_value = [comp_visible]

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["complexity"], comp_visible.complexity)
        self.assertEqual(len(data[0]["conditioners"]), 0)
        section_names = [s["name"] for s in data[0]["sections"]]
        self.assertNotIn(sec_hidden.name, section_names)

    def test_conditioner_linked_via_axis(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1)
        section = IdeologySectionFactory(
            abstraction_complexity=complexity, add_axes__total=0
        )
        axis = IdeologyAxisFactory(section=section)
        cond = IdeologyConditionerFactory()

        IdeologyAxisConditioner.objects.create(
            axis=axis, conditioner=cond, name="AxisRule"
        )
        UserConditionerAnswerFactory(user=self.user, conditioner=cond, answer="Yes")

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers
        self.assertEqual(len(data[0]["conditioners"]), 1)
