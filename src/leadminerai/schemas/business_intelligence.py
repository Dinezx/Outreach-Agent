from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class PainPointPrediction(BaseModel):
    name: str
    severity: int = Field(default=80, ge=0, le=100)
    frequency: str = "Daily"
    confidence: int = Field(default=80, ge=0, le=100)


class DepartmentPrediction(BaseModel):
    name: str
    confidence: int = Field(default=80, ge=0, le=100)


class BusinessIntelligenceRead(BaseModel):
    id: str
    company_id: str
    company_name: str | None = None
    industry: str | None = None
    sub_industry: str | None = None
    description: str | None = None
    products: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    manufacturing_type: str | None = None
    departments: list[DepartmentPrediction] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    markets: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    predicted_pain_points: list[PainPointPrediction] = Field(default_factory=list)
    confidence: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessIntelligenceAnalyzeRequest(BaseModel):
    company_id: str


class BusinessIntelligenceAnalyzeResponse(BaseModel):
    success: bool
    message: str
    intelligence: BusinessIntelligenceRead | None = None


class BusinessIntelligenceAnalyzeAllResponse(BaseModel):
    queued: int
    message: str


class BusinessIntelligenceListResponse(BaseModel):
    total: int
    items: list[BusinessIntelligenceRead]
