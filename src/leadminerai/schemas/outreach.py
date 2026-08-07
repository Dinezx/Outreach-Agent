from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from leadminerai.models.enums import OutreachStatus


class OutreachHistoryRead(BaseModel):
    id: str
    campaign_id: str
    action: str
    notes: str | None = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class OutreachCampaignRead(BaseModel):
    id: str
    company_id: str
    company_name: str | None = None
    contact_id: str | None = None
    contact_value: str | None = None
    decision_maker_id: str | None = None
    decision_maker_name: str | None = None
    decision_maker_designation: str | None = None
    channel: str
    target_role: str | None = None
    subject: str | None = None
    email_body: str | None = None
    linkedin_message: str | None = None
    phone_script: str | None = None
    recommendation_reason: str | None = None
    channel_confidence: int = 0
    overall_confidence: int = 0
    status: OutreachStatus
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    rejection_reason: str | None = None
    generation_time_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    history: list[OutreachHistoryRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutreachGenerateRequest(BaseModel):
    company_id: str


class OutreachGenerateResponse(BaseModel):
    success: bool
    message: str
    campaign: OutreachCampaignRead | None = None


class OutreachGenerateAllResponse(BaseModel):
    queued: int
    message: str


class OutreachApproveRequest(BaseModel):
    notes: str | None = None


class OutreachRejectRequest(BaseModel):
    reason: str | None = None


class OutreachEditRequest(BaseModel):
    subject: str | None = None
    email_body: str | None = None
    linkedin_message: str | None = None
    phone_script: str | None = None


class OutreachScheduleRequest(BaseModel):
    scheduled_at: datetime


class OutreachListResponse(BaseModel):
    total: int
    items: list[OutreachCampaignRead]
