from typing import Any

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
from ideology.models import (
    CompletedAnswer,
    IdeologyAxisConditioner,
    IdeologyConditionerConditioner,
    IdeologySectionConditioner,
)


class CompletedAnswerManagerTestCase(TestCase):
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

        completed = CompletedAnswer.objects.generate_snapshot(self.user)
        data = completed.answers[0]

        self.assertEqual(len(data["conditioners"]), 2)
        names = sorted([c["name"] for c in data["conditioners"]])
        self.assertEqual(names, ["CondAxis", "CondSection"])

    def test_recursive_dependency_scenarios(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1)
        section = IdeologySectionFactory(
            abstraction_complexity=complexity, add_axes__total=0
        )

        scenarios: list[dict[str, Any]] = [
            {
                "name": "Linear Chain (C1->C2->C3)",
                "setup": lambda: self._setup_linear_chain(section),
                "expected_conditioners": ["C1", "C2", "C3"],
            },
            {
                "name": "Redundant Branches",
                "setup": lambda: self._setup_redundant_branches(section),
                "expected_conditioners": ["Base", "Redundant"],
                "unexpected_conditioners": ["OrphanTgt"],
            },
        ]

        for scenario in scenarios:
            with self.subTest(scenario=scenario["name"]):
                UserConditionerAnswerFactory._meta.model.objects.all().delete()
                IdeologyConditionerConditioner.objects.all().delete()
                IdeologySectionConditioner.objects.all().delete()

                scenario["setup"]()

                completed = CompletedAnswer.objects.generate_snapshot(self.user)
                data = completed.answers[0]
                names = [c["name"] for c in data["conditioners"]]

                for expected in scenario.get("expected_conditioners", []):
                    self.assertIn(expected, names)

                for unexpected in scenario.get("unexpected_conditioners", []):
                    self.assertNotIn(unexpected, names)

    def _setup_linear_chain(self, section):
        c1 = IdeologyConditionerFactory(name="C1")
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=c1, name="Rule-C1"
        )
        c2 = IdeologyConditionerFactory(name="C2")
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=c2, source_conditioner=c1, name="Rule-C2-C1"
        )
        c3 = IdeologyConditionerFactory(name="C3")
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=c3, source_conditioner=c2, name="Rule-C3-C2"
        )
        UserConditionerAnswerFactory(user=self.user, conditioner=c1, answer="Yes")
        UserConditionerAnswerFactory(user=self.user, conditioner=c2, answer="Yes")
        UserConditionerAnswerFactory(user=self.user, conditioner=c3, answer="Yes")

    def _setup_redundant_branches(self, section):
        c_orphan_src = IdeologyConditionerFactory(name="OrphanSrc")
        c_orphan_tgt = IdeologyConditionerFactory(name="OrphanTgt")
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=c_orphan_tgt,
            source_conditioner=c_orphan_src,
            name="RuleOrphan",
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=c_orphan_tgt, answer="A"
        )

        c_base = IdeologyConditionerFactory(name="Base")
        c_redundant = IdeologyConditionerFactory(name="Redundant")
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=c_base, name="R1"
        )
        IdeologySectionConditioner.objects.create(
            section=section, conditioner=c_redundant, name="R2"
        )
        IdeologyConditionerConditioner.objects.create(
            target_conditioner=c_redundant,
            source_conditioner=c_base,
            name="RuleRedundant",
        )
        UserConditionerAnswerFactory(
            user=self.user, conditioner=c_redundant, answer="B"
        )

    def test_multiple_axes_same_section(self):
        complexity = IdeologyAbstractionComplexityFactory(complexity=1)
        section = IdeologySectionFactory(
            abstraction_complexity=complexity, name="Economy"
        )

        axis_1 = IdeologyAxisFactory(section=section, name="Market")
        axis_2 = IdeologyAxisFactory(section=section, name="Regulation")

        UserAxisAnswerFactory(user=self.user, axis=axis_1, value=10)
        UserAxisAnswerFactory(user=self.user, axis=axis_2, value=-10)

        completed = CompletedAnswer.objects.generate_snapshot(self.user)
        data = completed.answers[0]

        self.assertEqual(len(data["sections"]), 1)
        axes_list = data["sections"][0]["axes"]
        self.assertEqual(len(axes_list), 2)

        names = sorted([a["name"] for a in axes_list])
        self.assertEqual(names, ["Market", "Regulation"])
