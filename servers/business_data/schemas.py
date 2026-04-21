from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CaseStatusLiteral = Literal[
    "new",
    "in_progress",
    "pending_review",
    "approved",
    "rejected",
    "blocked",
]


class GetCaseStatusInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class CaseStatusOutput(BaseModel):
    case_id: str
    status: CaseStatusLiteral
    substatus: str | None = None
    owner_team: str | None = None
    updated_at: str
    next_action: str | None = None
    source_system: str = "kvbb-core"


class SearchCasesFilters(BaseModel):
    customer_id: str | None = None
    statuses: list[CaseStatusLiteral] | None = None
    created_after: str | None = None


class SearchCasesInput(BaseModel):
    filters: SearchCasesFilters
    limit: int = Field(default=20, ge=1, le=100)


class SearchCaseItem(BaseModel):
    case_id: str
    status: CaseStatusLiteral
    created_at: str


class SearchCasesOutput(BaseModel):
    items: list[SearchCaseItem]
    count: int