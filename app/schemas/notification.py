from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    notification_type: str = Field(..., alias="notification-type")
    message: str
    details: dict[str, Any]
    is_read: bool = Field(..., alias="is-read")
    created_at: datetime = Field(..., alias="created-at")


class NotificationListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    notifications: list[NotificationResponse]
    unread_count: int = Field(..., alias="unread-count")


class UnreadCountResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    unread_count: int = Field(..., alias="unread-count")
