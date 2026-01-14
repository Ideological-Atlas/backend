from core.factories import UserFactory
from django.test import TestCase
from ideology.factories import (
    AxisAnswerFactory,
    ConditionerAnswerFactory,
    IdeologyAbstractionComplexityFactory,
    IdeologyAxisFactory,
    IdeologyConditionerFactory,
    IdeologySectionFactory,
)
from ideology.models import IdeologySectionConditioner
from ideology.services import AnswerService


class AnswerServiceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_generate_snapshot_deterministic(self):
        scenarios = [
            (
                "Minimal Structure",
                {"complexities": 1, "sections": 1, "axes": 1, "conditioners": 0},
            ),
            (
                "Complex Structure",
                {"complexities": 2, "sections": 2, "axes": 2, "conditioners": 2},
            ),
        ]

        for name, config in scenarios:
            with self.subTest(name=name):
                self._run_scenario(config)

    def _run_scenario(self, config):
        self.user.axis_results.all().delete()
        self.user.conditioner_answers.all().delete()

        complexities = []
        for i in range(config["complexities"]):
            complexities.append(
                IdeologyAbstractionComplexityFactory(
                    complexity=i + 1, name=f"Level-{i+1}"
                )
            )

        for complexity in complexities:
            sections = []
            for j in range(config["sections"]):
                sections.append(
                    IdeologySectionFactory(
                        abstraction_complexity=complexity,
                        name=f"Sec-{complexity.complexity}-{j}",
                        add_axes__total=0,
                    )
                )

            for section in sections:
                for k in range(config["axes"]):
                    axis = IdeologyAxisFactory(section=section, name=f"Axis-{k}")
                    AxisAnswerFactory(user=self.user, axis=axis, value=50)

                for m in range(config["conditioners"]):
                    cond = IdeologyConditionerFactory(name=f"Cond-{m}")
                    IdeologySectionConditioner.objects.create(
                        section=section, conditioner=cond, name=f"Rule-{m}"
                    )
                    ConditionerAnswerFactory(
                        user=self.user, conditioner=cond, answer="Yes"
                    )

        completed = AnswerService.generate_snapshot(self.user)
        data = completed.answers

        self.assertEqual(len(data), config["complexities"])

        for comp_data in data:
            self.assertEqual(len(comp_data["sections"]), config["sections"])
            expected_conditioners_per_level = (
                config["sections"] * config["conditioners"]
            )
            self.assertEqual(
                len(comp_data["conditioners"]), expected_conditioners_per_level
            )

            for sect_data in comp_data["sections"]:
                self.assertEqual(len(sect_data["axes"]), config["axes"])
