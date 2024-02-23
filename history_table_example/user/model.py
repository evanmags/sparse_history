from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from history_table_example.database import BaseModel


class UserHistoryLayerModel(BaseModel):
    __tablename__ = "users"
    __table_args__ = (Index("idx_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), nullable=False, server_default=func.gen_random_uuid()
    )
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    company: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
