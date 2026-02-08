from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from ideology.services.calculation_dto import CalculationItem


def get_conditioner_complexity_annotation(prefix="conditioner"):
    p = f"{prefix}__" if prefix else ""
    return Coalesce(
        F(f"{p}conditioned_sections__abstraction_complexity__uuid"),
        F(f"{p}conditioned_axes__section__abstraction_complexity__uuid"),
        output_field=models.UUIDField(),
    )


def format_mapped_item(**kwargs) -> CalculationItem:
    if "item_type" in kwargs:
        kwargs["type"] = kwargs.pop("item_type")
    return CalculationItem(**kwargs)
