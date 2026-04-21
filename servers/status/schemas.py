from __future__ import annotations

from pydantic import BaseModel, Field


class GetWorkflowStatusInput(BaseModel):
    workflow_id: str = Field(..., min_length=1)


class GetWorkflowStatusOutput(BaseModel):
    workflow_id: str
    status: str
    current_step: str | None = None
    updated_at: str


class GetProcessingSummaryInput(BaseModel):
    case_id: str = Field(..., min_length=1)


class GetProcessingSummaryOutput(BaseModel):
    case_id: str
    workflow_status: str
    case_status: str
    next_action: str | None = None