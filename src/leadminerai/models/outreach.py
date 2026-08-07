from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from leadminerai.models.base import Base
from leadminerai.models.enums import OutreachStatus


class OutreachCampaign(Base):
    __tablename__ = "outreach_campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("company_contacts.id", ondelete="SET NULL"), nullable=True
    )
    decision_maker_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("decision_makers.id", ondelete="SET NULL"), nullable=True
    )
    channel: Mapped[str] = mapped_column(String(100), nullable=False, default="office_email")
    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_script: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel_confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[OutreachStatus] = mapped_column(
        Enum(OutreachStatus, name="outreach_status", native_enum=False),
        default=OutreachStatus.PENDING_APPROVAL,
        nullable=False,
        index=True
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    company = relationship("Company", backref=backref("outreach_campaigns", cascade="all, delete-orphan"))
    contact = relationship("CompanyContact")
    decision_maker = relationship("DecisionMaker")
    history = relationship("OutreachHistory", back_populates="campaign", cascade="all, delete-orphan", order_by="OutreachHistory.timestamp.asc()")


class OutreachHistory(Base):
    __tablename__ = "outreach_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outreach_campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    campaign = relationship("OutreachCampaign", back_populates="history")
