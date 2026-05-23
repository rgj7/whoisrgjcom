import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class PostBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content: dict = Field(...)
    excerpt: str | None = Field(default=None, max_length=500)
    published: bool = True
    tags: list[str] = []

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, value):
        """Convert Tag ORM objects to tag name strings."""
        if value is None:
            return []
        return [
            tag.name if hasattr(tag, "name") else tag
            for tag in value
        ]


class PostCreate(PostBase):
    """Schema for creating a new post."""

    pass


class PostUpdate(BaseModel):
    """Schema for updating an existing post (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    content: dict | None = Field(default=None)
    excerpt: str | None = Field(default=None, max_length=500)
    published: bool | None = None
    tags: list[str] | None = None


class PostResponse(PostBase):
    """Schema returned by the API."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID):
        return str(value)

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, value: datetime):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=ZoneInfo("UTC"))
            return value.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value

    @field_serializer("tags")
    def serialize_tags(self, value: list[str]):
        return sorted(value)


class PaginatedPosts(BaseModel):
    """Paginated response for the posts list."""

    items: list[PostResponse]
    total: int
    page: int
    limit: int
    pages: int
