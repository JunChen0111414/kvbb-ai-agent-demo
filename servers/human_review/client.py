from __future__ import annotations

from datetime import UTC, datetime


class HumanReviewClient:
    def create_task(self, case_id: str, review_type: str, payload: dict) -> dict:
        return {
            "task_id": "review-555",
            "queue": "ops-review",
            "status": "created",
            "created_at": datetime.now(UTC).isoformat(),
        }

    def submit_decision(self, task_id: str, decision: str, comment: str | None) -> dict:
        return {
            "task_id": task_id,
            "status": decision,
            "updated_at": datetime.now(UTC).isoformat(),
        }
