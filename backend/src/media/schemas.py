import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class MediaResponse(BaseModel):
    """Schema returned by the media API."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    url: str = Field(validation_alias="public_url")
    object_name: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID):
        return str(value)

    @field_serializer("created_at")
    def serialize_dt(self, value: datetime):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))
            return value.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value
