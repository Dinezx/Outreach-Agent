from __future__ import annotations

from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from leadminerai.models.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    messages: Mapped[list[GmailMessage]] = relationship("GmailMessage", back_populates="account", cascade="all, delete-orphan")


class GmailMessage(Base):
    __tablename__ = "gmail_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    company_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    contact_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("company_contacts.id", ondelete="SET NULL"), nullable=True)
    decision_maker_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("decision_makers.id", ondelete="SET NULL"), nullable=True)
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True)
    gmail_account_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("gmail_accounts.id", ondelete="SET NULL"), nullable=True)

    gmail_message_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    history_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    recipient_email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    sender_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status: DRAFT, APPROVED, SENDING, SENT, FAILED, REPLIED, FOLLOW_UP, CLOSED
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", index=True, nullable=False)

    is_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reply_from: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reply_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    follow_up_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scheduled_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    company = relationship("Company", foreign_keys=[company_id])
    contact = relationship("CompanyContact", foreign_keys=[contact_id])
    decision_maker = relationship("DecisionMaker", foreign_keys=[decision_maker_id])
    campaign = relationship("OutreachCampaign", foreign_keys=[campaign_id])
    account = relationship("GmailAccount", back_populates="messages")
