from __future__ import annotations

from datetime import UTC, datetime


class StatusClient:
    def get_workflow_status(self, workflow_id: str) -> dict:
        return {
            "workflow_id": workflow_id,
            "status": "running",
            "current_step": "document_check",
            "updated_at": datetime.now(UTC).isoformat(),
        }

    def get_processing_summary(self, case_id: str) -> dict:
        return {
            "case_id": case_id,
            "workflow_status": "running",
            "case_status": "pending_review",
            "next_action": "human_review",
        }