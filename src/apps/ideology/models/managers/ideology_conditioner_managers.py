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
                | Q(source_axis__section__abstraction_complexity__uuid=complexity_uuid)
            ).values_list("id", flat=True)
        )

        current_pool = list(relevant_ids)

        while current_pool:
            new_ids = set()

            parents = IdeologyConditionerConditioner.objects.filter(
                target_conditioner__id__in=current_pool
            ).values_list("conditioner_id", flat=True)

            children = IdeologyConditionerConditioner.objects.filter(
                conditioner__id__in=current_pool
            ).values_list("target_conditioner_id", flat=True)

            potential_new = set(parents) | set(children)
            new_ids = potential_new - relevant_ids

            if not new_ids:
                break

            relevant_ids.update(new_ids)
            current_pool = list(new_ids)

        return self.filter(id__in=relevant_ids).order_by("created")
