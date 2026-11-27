"""Schema Pydantic của API, khớp codebase/web/src/api/types.ts (TripInput)."""
from typing import Optional

from pydantic import BaseModel


class TripInput(BaseModel):
    headcount: Optional[int] = None
    days: Optional[int] = None
    start_date: Optional[str] = None
    origin: str = ""
    purpose: Optional[str] = None
    budget: Optional[int] = None
    budget_per_person: bool = False
    destination: str = ""
