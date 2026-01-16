import factory
from core.factories import TimeStampedUUIDModelFactory, add_related_conditioners
from ideology.models import IdeologyConditioner, IdeologyConditionerConditioner


class IdeologyConditionerFactory(TimeStampedUUIDModelFactory):
    class Meta:
        model = IdeologyConditioner

    name = factory.Sequence(lambda n: f"Conditioner-{n}")
    description = factory.Faker("sentence")
    type = IdeologyConditioner.ConditionerType.CATEGORICAL
    accepted_values = ["Option A", "Option B", "Option C"]

    @factory.post_generation
    def add_conditioners(self, create, extracted, **kwargs):
        add_related_conditioners(
            obj=self,
            create=create,
            extracted=extracted,
            through_model=IdeologyConditionerConditioner,
            parent_field="target_conditioner",
            child_field="source_conditioner",
            name_prefix="CondRule",
            **kwargs,
        )
