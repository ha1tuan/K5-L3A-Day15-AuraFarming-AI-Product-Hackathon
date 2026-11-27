"""Schema Pydantic của API, khớp codebase/web/src/api/types.ts (TripInput)."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.core.planning.types import Tier


class TripInput(BaseModel):
    headcount: Optional[int] = None
    days: Optional[int] = None
    start_date: Optional[str] = None
    origin: str = ""
    purpose: Optional[str] = None
    budget: Optional[int] = None
    budget_per_person: bool = False
    destination: str = ""


class ApproveInput(BaseModel):
    destination: Optional[str] = None
    package: Tier
    headcount: Optional[int] = None
    remove_items: list[Literal["gala", "team_building"]] = Field(default_factory=list)
