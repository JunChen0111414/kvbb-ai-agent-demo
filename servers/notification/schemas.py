from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


ChannelLiteral = Literal["email"]


class SendNotificationInput(BaseModel):
    recipient: EmailStr
    channel: ChannelLiteral = "email"
    template_id: str = Field(..., min_length=1)
    variables: dict


class SendNotificationOutput(BaseModel):
    success: bool
    message_id: str
    sent_at: str


class PreviewNotificationInput(BaseModel):
    template_id: str
    variables: dict


class PreviewNotificationOutput(BaseModel):
    subject: str
    body: str