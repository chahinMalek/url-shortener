from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class ShortenRequest(BaseModel):
    long_url: HttpUrl = Field(..., alias="long-url", description="The URL to shorten")
    expires: datetime | None = Field(default=None, description="Expiration datetime")

    class Config:
        populate_by_name = True


class ShortenResponse(BaseModel):
    long_url: str = Field(..., alias="long-url", description="The original URL")
    short_url: str = Field(..., alias="short-url", description="The shortened URL code")
    created_at: datetime = Field(..., alias="created-at", description="Creation timestamp")
    is_active: bool = Field(
        ..., alias="is-active", description="Whether the shortened URL is active"
    )

    class Config:
        populate_by_name = True
