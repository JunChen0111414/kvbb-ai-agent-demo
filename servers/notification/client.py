from __future__ import annotations

from datetime import UTC, datetime


class NotificationClient:
    def send(self, recipient: str, template_id: str, variables: dict) -> dict:
        return {
            "success": True,
            "message_id": "mail-789",
            "sent_at": datetime.now(UTC).isoformat(),
        }

    def preview(self, template_id: str, variables: dict) -> dict:
        return {
            "subject": f"[{template_id}] Update",
            "body": f"Rendered with variables: {variables}",
        }