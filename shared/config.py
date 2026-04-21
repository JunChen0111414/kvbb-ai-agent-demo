from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BusinessDataConfig:
    db_url: str
    db_schema: str = "public"


@dataclass(frozen=True)
class NotificationConfig:
    mail_api_base: str
    mail_api_key: str


@dataclass(frozen=True)
class StatusConfig:
    status_api_base: str
    status_api_token: str


@dataclass(frozen=True)
class HumanReviewConfig:
    review_api_base: str
    review_api_token: str


def get_business_data_config() -> BusinessDataConfig:
    return BusinessDataConfig(
        db_url=os.environ["DB_URL"],
        db_schema=os.environ.get("DB_SCHEMA", "public"),
    )


def get_notification_config() -> NotificationConfig:
    return NotificationConfig(
        mail_api_base=os.environ["MAIL_API_BASE"],
        mail_api_key=os.environ["MAIL_API_KEY"],
    )


def get_status_config() -> StatusConfig:
    return StatusConfig(
        status_api_base=os.environ["STATUS_API_BASE"],
        status_api_token=os.environ["STATUS_API_TOKEN"],
    )


def get_human_review_config() -> HumanReviewConfig:
    return HumanReviewConfig(
        review_api_base=os.environ["REVIEW_API_BASE"],
        review_api_token=os.environ["REVIEW_API_TOKEN"],
    )