from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from leadminerai.models.base import Base


class CompanyBusinessIntelligence(Base):
    __tablename__ = "company_business_intelligence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    industry: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    sub_industry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    products: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    services: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    manufacturing_type: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    departments: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    locations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    certifications: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    markets: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    pain_points: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", backref=backref("business_intelligence", uselist=False, cascade="all, delete-orphan"))
