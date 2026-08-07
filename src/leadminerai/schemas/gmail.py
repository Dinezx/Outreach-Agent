from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class GmailAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class GmailMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str | None = None
    company_name: str | None = None
    contact_id: str | None = None
    decision_maker_id: str | None = None
    campaign_id: str | None = None
    gmail_account_id: str | None = None
    gmail_message_id: str | None = None
    thread_id: str | None = None
    history_id: str | None = None
    subject: str | None = None
    body: str | None = None
    recipient_email: str | None = None
    sender_email: str | None = None
    status: str
    is_reply: bool = False
    reply_from: str | None = None
    reply_body: str | None = None
    replied_at: datetime | None = None
    follow_up_count: int = 0
    scheduled_follow_up_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class GmailSendRequest(BaseModel):
    company_id: str | None = None
    contact_id: str | None = None
    decision_maker_id: str | None = None
    campaign_id: str | None = None
    recipient_email: str
    subject: str
    body: str
    thread_id: str | None = None


class GmailSendBulkRequest(BaseModel):
    campaign_ids: list[str] = Field(default_factory=list)


class GmailFollowUpRequest(BaseModel):
    follow_up_days: int = Field(default=3, description="3-day, 7-day, or 14-day follow up")
    body: str | None = None


class GmailPollRepliesResponse(BaseModel):
    checked_threads: int
    new_replies: int
    message: str


class GmailListResponse(BaseModel):
    total: int
    items: list[GmailMessageRead]
