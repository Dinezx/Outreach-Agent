from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


# Compatibility Schemas (Old flat column layout)
class ContactBase(BaseModel):
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    linkedin: str | None = None
    facebook: str | None = None
    instagram: str | None = None
    youtube: str | None = None
    contact_page: str | None = None
    maps_url: str | None = None
    confidence_score: int = 0


class ContactRead(ContactBase):
    id: str
    company_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContactDetailedRead(ContactRead):
    company_name: str


# Sprint 3 Intelligence Schemas (One-to-many layout)
class CompanyContactRead(BaseModel):
    id: str
    company_id: str
    contact_type: str
    contact_value: str
    contact_label: str
    priority: int
    confidence: int
    source_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DecisionMakerRead(BaseModel):
    id: str
    company_id: str
    name: str
    designation: str
    linkedin_url: str | None = None
    source_url: str | None = None
    priority: int
    confidence: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyIntelligenceRead(BaseModel):
    company_id: str
    company_name: str
    industry: str | None = None
    contacts: list[CompanyContactRead]
    decision_makers: list[DecisionMakerRead]


class ContactExtractRequest(BaseModel):
    company_id: str


class ContactExtractResponse(BaseModel):
    success: bool
    message: str
    intelligence: CompanyIntelligenceRead | None = None
    contact: ContactRead | None = None  # Compatibility field


class ContactExtractAllResponse(BaseModel):
    queued: int
    message: str
