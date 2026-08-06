from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from leadminerai.models.enums import CompanyStatus


class CompanyRead(BaseModel):
    id: str
    name: str
    website_url: str | None
    status: CompanyStatus
    last_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    items: list[CompanyRead]
    total: int


class UploadResponse(BaseModel):
    created: int
    skipped: int
    total_received: int


class SearchTriggerRequest(BaseModel):
    company_ids: list[str] | None = Field(default=None, description="Optional target company ids")


class SearchTriggerResponse(BaseModel):
    queued: int
