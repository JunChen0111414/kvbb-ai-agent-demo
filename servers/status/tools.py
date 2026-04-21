from __future__ import annotations

from servers.status.client import StatusClient
from servers.status.schemas import (
    GetProcessingSummaryInput,
    GetProcessingSummaryOutput,
    GetWorkflowStatusInput,
    GetWorkflowStatusOutput,
)

client = StatusClient()


def get_workflow_status(payload: dict) -> dict:
    data = GetWorkflowStatusInput.model_validate(payload)
    result = client.get_workflow_status(data.workflow_id)
    return GetWorkflowStatusOutput.model_validate(result).model_dump()


def get_processing_summary(payload: dict) -> dict:
    data = GetProcessingSummaryInput.model_validate(payload)
    result = client.get_processing_summary(data.case_id)
    return GetProcessingSummaryOutput.model_validate(result).model_dump()