import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class TravelResponse(BaseModel):
    """Single travel record."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    country_code: str
    status: str
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


class TravelsResponse(BaseModel):
    """Public response: two flat lists of country codes."""

    visited: list[str] = Field(default_factory=list)
    bucketlist: list[str] = Field(default_factory=list)


class TravelsBatchCreate(BaseModel):
    """Admin batch-replace payload."""

    visited: list[str] = Field(default_factory=list)
    bucketlist: list[str] = Field(default_factory=list)
