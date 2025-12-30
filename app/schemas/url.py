from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ShortenRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    long_url: HttpUrl = Field(..., alias="long-url", description="The URL to shorten")
    expires: datetime | None = Field(default=None, description="Expiration datetime")


class ShortenResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    long_url: str = Field(..., alias="long-url", description="The original URL")
    short_url: str = Field(..., alias="short-url", description="The shortened URL code")
    created_at: datetime = Field(..., alias="created-at", description="Creation timestamp")
    is_active: bool = Field(
        ..., alias="is-active", description="Whether the shortened URL is active"
    )
