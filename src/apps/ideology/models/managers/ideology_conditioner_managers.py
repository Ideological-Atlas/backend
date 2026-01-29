from django.db import models
from django.db.models import Q


class IdeologyConditionerManager(models.Manager):
    def get_by_complexity(self, complexity_uuid: str):
        from ideology.models import IdeologyConditionerConditioner

        relevant_ids = set(
            self.filter(
                Q(
                    ideologysectionconditioner_rules__section__abstraction_complexity__uuid=complexity_uuid
                )
                | Q(
                    ideologyaxisconditioner_rules__axis__section__abstraction_complexity__uuid=complexity_uuid
                )
            ).values_list("id", flat=True)
        )

        current_level_ids = list(relevant_ids)

        while current_level_ids:
            parent_dependencies = IdeologyConditionerConditioner.objects.filter(
                target_conditioner__id__in=current_level_ids
            ).values_list("conditioner_id", flat=True)

            new_parent_ids = set(parent_dependencies) - relevant_ids

            if not new_parent_ids:
                break

            relevant_ids.update(new_parent_ids)
            current_level_ids = list(new_parent_ids)

        return self.filter(id__in=relevant_ids).order_by("created")
