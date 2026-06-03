import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_serializer, field_validator


class SocialLinkBase(BaseModel):
    platform: str = Field(min_length=1, max_length=50)
    url: AnyHttpUrl = Field(max_length=500)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("platform")
    @classmethod
    def strip_platform(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Platform is required")
        return value

    @field_serializer("url")
    def serialize_url(self, value: AnyHttpUrl) -> str:
        return str(value)


class SocialLinkCreate(SocialLinkBase):
    pass


class SocialLinksBatchCreate(BaseModel):
    links: list[SocialLinkCreate] = Field(default_factory=list)


class SocialLinkResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    platform: str
    url: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, value: datetime) -> str:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))
            return value.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value


class SocialLinksResponse(BaseModel):
    links: list[SocialLinkResponse] = Field(default_factory=list)
