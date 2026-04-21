from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DecisionLiteral = Literal["approved", "rejected", "needs_more_info"]


class CreateReviewTaskInput(BaseModel):
    case_id: str = Field(..., min_length=1)
    review_type: str = Field(..., min_length=1)
    payload: dict


class CreateReviewTaskOutput(BaseModel):
    task_id: str
    queue: str
    status: str
    created_at: str


class SubmitReviewDecisionInput(BaseModel):
    task_id: str = Field(..., min_length=1)
    decision: DecisionLiteral
    comment: str | None = None


class SubmitReviewDecisionOutput(BaseModel):
    task_id: str
    status: str
    updated_at: str
