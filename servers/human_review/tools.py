from __future__ import annotations

from servers.human_review.client import HumanReviewClient
from servers.human_review.schemas import (
    CreateReviewTaskInput,
    CreateReviewTaskOutput,
    SubmitReviewDecisionInput,
    SubmitReviewDecisionOutput,
)

client = HumanReviewClient()


def create_review_task(payload: dict) -> dict:
    data = CreateReviewTaskInput.model_validate(payload)
    result = client.create_task(
        case_id=data.case_id,
        review_type=data.review_type,
        payload=data.payload,
    )
    return CreateReviewTaskOutput.model_validate(result).model_dump()


def submit_review_decision(payload: dict) -> dict:
    data = SubmitReviewDecisionInput.model_validate(payload)
    result = client.submit_decision(
        task_id=data.task_id,
        decision=data.decision,
        comment=data.comment,
    )
    return SubmitReviewDecisionOutput.model_validate(result).model_dump()
