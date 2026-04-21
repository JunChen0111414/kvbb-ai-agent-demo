from __future__ import annotations

from servers.notification.client import NotificationClient
from servers.notification.schemas import (
    PreviewNotificationInput,
    PreviewNotificationOutput,
    SendNotificationInput,
    SendNotificationOutput,
)

client = NotificationClient()


def send_notification(payload: dict) -> dict:
    data = SendNotificationInput.model_validate(payload)
    result = client.send(
        recipient=str(data.recipient),
        template_id=data.template_id,
        variables=data.variables,
    )
    return SendNotificationOutput.model_validate(result).model_dump()


def preview_notification(payload: dict) -> dict:
    data = PreviewNotificationInput.model_validate(payload)
    result = client.preview(
        template_id=data.template_id,
        variables=data.variables,
    )
    return PreviewNotificationOutput.model_validate(result).model_dump()