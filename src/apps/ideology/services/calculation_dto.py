from typing import Any, Literal, Optional

from pydantic import BaseModel


class CalculationItem(BaseModel):
    type: Literal["axis", "conditioner"]
    value: Any
    is_indifferent: bool = False
    complexity_uuid: Optional[str] = None
    section_uuid: Optional[str] = None
    margin_left: int = 0
    margin_right: int = 0
