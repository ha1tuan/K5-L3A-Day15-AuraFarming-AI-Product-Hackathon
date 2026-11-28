"""Schema Pydantic của API, khớp codebase/web/src/api/types.ts (TripInput)."""
from typing import Dict, List, Literal, Optional

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
    package: str = "can_bang"
    headcount: Optional[int] = None
    remove_items: Optional[List[str]] = None


class QuoteInput(BaseModel):
    text: str


class ChatInput(BaseModel):
    messages: List[Dict[str, str]]


class RecalcInput(BaseModel):
    headcount: Optional[int] = None
    days: Optional[int] = None
    removed: Optional[List[str]] = None


class TripQuoteInput(BaseModel):
    text: str
    tier: str = "can_bang"


class MoreDestinationsInput(BaseModel):
    exclude: List[str] = Field(default_factory=list)
