import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Travel(Base):
    __tablename__ = "travel"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    country_code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('visited', 'bucketlist')", name="travel_status_check"),
        nullable=False,
        default="bucketlist",
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
