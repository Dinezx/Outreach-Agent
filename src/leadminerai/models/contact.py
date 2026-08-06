from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from leadminerai.models.base import Base


class CompanyContact(Base):
    __tablename__ = "company_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_type: Mapped[str] = mapped_column(String(100), nullable=False)  # email, phone, social, address, map
    contact_value: Mapped[str] = mapped_column(Text, nullable=False)
    contact_label: Mapped[str] = mapped_column(String(255), nullable=False)  # sales@, Toll Free, LinkedIn, etc.
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", backref=backref("contacts", cascade="all, delete-orphan"))
