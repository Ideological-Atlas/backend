def add_related_conditioners(
    obj,
    create,
    extracted,
    through_model,
    parent_field,
    child_field="conditioner",
    name_prefix="Rule",
    **kwargs,
):
    if not create:
        return

    from ideology.factories.ideology_conditioner_factory import (
        IdeologyConditionerFactory,
    )

    if extracted:
        for item in extracted:
            valid_val = item.accepted_values[0] if item.accepted_values else "true"

            create_kwargs = {
                parent_field: obj,
                child_field: item,
                "name": f"{name_prefix}-{item.name}",
                "condition_values": [valid_val],
            }
            through_model.objects.create(**create_kwargs)
        return

    count = kwargs.get("total", 0)
    if count:
        for i in range(count):
            item = IdeologyConditionerFactory()
            valid_val = item.accepted_values[0] if item.accepted_values else "true"

            create_kwargs = {
                parent_field: obj,
                child_field: item,
                "name": f"{name_prefix}-Auto-{i}",
                "condition_values": [valid_val],
            }
            through_model.objects.create(**create_kwargs)
