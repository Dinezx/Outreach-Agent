from __future__ import annotations

import asyncio
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from leadminerai.api.deps import get_settings, get_session
from leadminerai.core.config import Settings
from leadminerai.core.database import DatabaseManager
from leadminerai.schemas.business_intelligence import (
    BusinessIntelligenceAnalyzeResponse,
    BusinessIntelligenceAnalyzeAllResponse,
    BusinessIntelligenceRead,
    BusinessIntelligenceListResponse,
    PainPointPrediction,
    DepartmentPrediction,
)
from leadminerai.repositories.business_intelligence_repository import BusinessIntelligenceRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.business_extractor_service import BusinessExtractorService
from leadminerai.services.export_service import ExportService
from leadminerai.agents.company_business_intelligence_agent import CompanyBusinessIntelligenceAgent

router = APIRouter()


def get_business_agent(request: Request, settings: Settings = Depends(get_settings)) -> CompanyBusinessIntelligenceAgent:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    crawler = CrawlerService()
    extractor = BusinessExtractorService(settings.openai_api_key)
    return CompanyBusinessIntelligenceAgent(database.sessionmaker, crawler, extractor)


def _to_read_schema(record, company_name: str | None = None) -> BusinessIntelligenceRead:
    comp_name = company_name or (record.company.name if getattr(record, "company", None) else None)
    
    depts = []
    for d in (record.departments or []):
        if isinstance(d, dict):
            depts.append(DepartmentPrediction(name=str(d.get("name", "")), confidence=int(d.get("confidence", 80))))
        else:
            depts.append(DepartmentPrediction(name=str(d), confidence=80))

    pains = []
    for p in (record.pain_points or []):
        if isinstance(p, dict):
            pains.append(
                PainPointPrediction(
                    name=str(p.get("name", "")),
                    severity=int(p.get("severity", 80)),
                    frequency=str(p.get("frequency", "Daily")),
                    confidence=int(p.get("confidence", 80))
                )
            )
        else:
            pains.append(PainPointPrediction(name=str(p), severity=80, frequency="Daily", confidence=80))

    return BusinessIntelligenceRead(
        id=record.id,
        company_id=record.company_id,
        company_name=comp_name,
        industry=record.industry,
        sub_industry=record.sub_industry,
        description=record.description,
        products=record.products or [],
        services=record.services or [],
        manufacturing_type=record.manufacturing_type,
        departments=depts,
        locations=record.locations or [],
        certifications=record.certifications or [],
        markets=record.markets or [],
        keywords=record.keywords or [],
        predicted_pain_points=pains,
        confidence=record.confidence,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.post("/analyze/{company_id}", response_model=BusinessIntelligenceAnalyzeResponse)
async def analyze_company_business_intelligence(
    company_id: str,
    session: AsyncSession = Depends(get_session),
    agent: CompanyBusinessIntelligenceAgent = Depends(get_business_agent),
) -> BusinessIntelligenceAnalyzeResponse:
    company_repo = CompanyRepository(session)
    companies = await company_repo.get_by_ids([company_id])
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[0]
    try:
        res = await agent.analyze_company(company.id)
        
        bi_repo = BusinessIntelligenceRepository(session)
        record = await bi_repo.get_by_company_id(company.id)
        if not record:
            raise HTTPException(status_code=500, detail="Failed to save business intelligence")

        schema_read = _to_read_schema(record, company.name)
        return BusinessIntelligenceAnalyzeResponse(
            success=True,
            message=f"Business intelligence analyzed successfully for {company.name}",
            intelligence=schema_read
        )
    except Exception as exc:
        logger.error(f"Business intelligence analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


async def run_analyze_all_background(database_sessionmaker, settings: Settings):
    logger.info("Starting background batch business intelligence analysis task")
    crawler = CrawlerService()
    extractor = BusinessExtractorService(settings.openai_api_key)
    agent = CompanyBusinessIntelligenceAgent(database_sessionmaker, crawler, extractor)
    await agent.analyze_all_companies()


@router.post("/analyze-all", response_model=BusinessIntelligenceAnalyzeAllResponse)
async def analyze_all_business_intelligence(
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> BusinessIntelligenceAnalyzeAllResponse:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")

    bi_repo = BusinessIntelligenceRepository(session)
    companies = await bi_repo.get_all_companies()

    if not companies:
        return BusinessIntelligenceAnalyzeAllResponse(
            queued=0,
            message="No companies found with valid website URLs"
        )

    background_tasks.add_task(run_analyze_all_background, database.sessionmaker, settings)
    return BusinessIntelligenceAnalyzeAllResponse(
        queued=len(companies),
        message=f"Queued background business intelligence analysis for {len(companies)} companies"
    )


@router.get("/export/csv")
async def export_business_intelligence_csv(
    industry: str | None = Query(default=None),
    city: str | None = Query(default=None),
    manufacturing_type: str | None = Query(default=None),
    predicted_pain: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> Any:
    bi_repo = BusinessIntelligenceRepository(session)
    records, _ = await bi_repo.list_intelligence(
        industry=industry,
        city=city,
        manufacturing_type=manufacturing_type,
        predicted_pain=predicted_pain,
        skip=0,
        limit=1000
    )
    
    items = []
    for r in records:
        schema = _to_read_schema(r)
        items.append(schema.model_dump())

    content = ExportService.build_business_intelligence_csv(items)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="business_intelligence.csv"'},
    )


@router.get("/export/excel")
async def export_business_intelligence_excel(
    industry: str | None = Query(default=None),
    city: str | None = Query(default=None),
    manufacturing_type: str | None = Query(default=None),
    predicted_pain: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> Any:
    bi_repo = BusinessIntelligenceRepository(session)
    records, _ = await bi_repo.list_intelligence(
        industry=industry,
        city=city,
        manufacturing_type=manufacturing_type,
        predicted_pain=predicted_pain,
        skip=0,
        limit=1000
    )
    
    items = []
    for r in records:
        schema = _to_read_schema(r)
        items.append(schema.model_dump())

    content = ExportService.build_business_intelligence_excel(items)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="business_intelligence.xlsx"'},
    )


@router.get("/export/json")
async def export_business_intelligence_json(
    industry: str | None = Query(default=None),
    city: str | None = Query(default=None),
    manufacturing_type: str | None = Query(default=None),
    predicted_pain: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> Any:
    bi_repo = BusinessIntelligenceRepository(session)
    records, _ = await bi_repo.list_intelligence(
        industry=industry,
        city=city,
        manufacturing_type=manufacturing_type,
        predicted_pain=predicted_pain,
        skip=0,
        limit=1000
    )
    
    items = []
    for r in records:
        schema = _to_read_schema(r)
        items.append(schema.model_dump())

    content = ExportService.build_business_intelligence_json(items)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="business_intelligence.json"'},
    )


@router.get("/{company_id}", response_model=BusinessIntelligenceRead)
async def get_business_intelligence_by_company(
    company_id: str,
    session: AsyncSession = Depends(get_session),
) -> BusinessIntelligenceRead:
    bi_repo = BusinessIntelligenceRepository(session)
    record = await bi_repo.get_by_company_id(company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Business intelligence profile not found for this company")
    return _to_read_schema(record)


@router.get("", response_model=BusinessIntelligenceListResponse)
async def list_business_intelligence(
    industry: str | None = Query(default=None),
    city: str | None = Query(default=None),
    manufacturing_type: str | None = Query(default=None),
    predicted_pain: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> BusinessIntelligenceListResponse:
    bi_repo = BusinessIntelligenceRepository(session)
    records, total = await bi_repo.list_intelligence(
        industry=industry,
        city=city,
        manufacturing_type=manufacturing_type,
        predicted_pain=predicted_pain,
        skip=skip,
        limit=limit
    )

    items = [_to_read_schema(r) for r in records]
    return BusinessIntelligenceListResponse(total=total, items=items)
