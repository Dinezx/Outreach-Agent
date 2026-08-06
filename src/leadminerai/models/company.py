from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from leadminerai.models.base import Base
from leadminerai.models.enums import CompanyStatus


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[CompanyStatus] = mapped_column(
        Enum(CompanyStatus, name="company_status", native_enum=False),
        default=CompanyStatus.PENDING,
        nullable=False,
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
