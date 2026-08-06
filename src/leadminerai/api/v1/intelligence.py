from __future__ import annotations

import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from leadminerai.api.deps import get_settings, get_session
from leadminerai.core.config import Settings
from leadminerai.core.database import DatabaseManager
from leadminerai.schemas.contact import (
    ContactExtractRequest,
    ContactExtractResponse,
    ContactExtractAllResponse,
    CompanyIntelligenceRead,
    CompanyContactRead,
    DecisionMakerRead,
)
from leadminerai.repositories.contact_repository import ContactRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.extractor_service import ExtractorService
from leadminerai.agents.contact_intelligence_agent import ContactIntelligenceAgent

router = APIRouter()


def get_intelligence_agent(request: Request, settings: Settings = Depends(get_settings)) -> ContactIntelligenceAgent:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    crawler = CrawlerService()
    extractor = ExtractorService(settings.openai_api_key)
    return ContactIntelligenceAgent(database.sessionmaker, crawler, extractor)


@router.post("/extract/{company_id}", response_model=ContactExtractResponse)
async def extract_company_intelligence(
    company_id: str,
    session: AsyncSession = Depends(get_session),
    agent: ContactIntelligenceAgent = Depends(get_intelligence_agent),
) -> ContactExtractResponse:
    company_repo = CompanyRepository(session)
    companies = await company_repo.get_by_ids([company_id])
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")
    
    company = companies[0]
    if not company.website_url:
        raise HTTPException(
            status_code=400,
            detail="Company does not have a website URL. Run website search first."
        )

    try:
        await agent.extract_intelligence(company.id, company.name, company.website_url)
        
        # Reload the saved data
        contact_repo = ContactRepository(session)
        intel = await contact_repo.get_company_intelligence(company.id)
        
        # Build Response Schema
        read_schema = CompanyIntelligenceRead(
            company_id=company.id,
            company_name=company.name,
            industry=None,
            contacts=[CompanyContactRead.model_validate(c) for c in intel["contacts"]],
            decision_makers=[DecisionMakerRead.model_validate(dm) for dm in intel["decision_makers"]],
        )

        return ContactExtractResponse(
            success=True,
            message="Company intelligence extracted successfully",
            intelligence=read_schema
        )
    except Exception as exc:
        logger.error(f"Intelligence extraction failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


async def run_extract_all_background(database_sessionmaker, settings: Settings):
    logger.info("Starting background bulk intelligence extraction task")
    crawler = CrawlerService()
    extractor = ExtractorService(settings.openai_api_key)
    agent = ContactIntelligenceAgent(database_sessionmaker, crawler, extractor)

    async with database_sessionmaker() as session:
        contact_repo = ContactRepository(session)
        companies = await contact_repo.get_companies_without_contacts()

    logger.info(f"Bulk intelligence extraction task queued {len(companies)} companies")
    for company in companies:
        if company.website_url:
            try:
                await agent.extract_intelligence(company.id, company.name, company.website_url)
            except Exception as exc:
                logger.error(f"Background intelligence extraction failed for {company.name}: {exc}")
            # Respect rate limits/concurrency limits
            await asyncio.sleep(1.0)


@router.post("/extract-all", response_model=ContactExtractAllResponse)
async def extract_all_intelligence(
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ContactExtractAllResponse:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
        
    contact_repo = ContactRepository(session)
    companies = await contact_repo.get_companies_without_contacts()
    
    if not companies:
        return ContactExtractAllResponse(
            queued=0,
            message="No companies found matching the criteria (has website, but intelligence empty)"
        )

    background_tasks.add_task(run_extract_all_background, database.sessionmaker, settings)
    return ContactExtractAllResponse(
        queued=len(companies),
        message=f"Queued background contact intelligence extraction for {len(companies)} companies"
    )


@router.get("/{company_id}", response_model=CompanyIntelligenceRead)
async def get_company_intelligence(
    company_id: str,
    session: AsyncSession = Depends(get_session),
) -> CompanyIntelligenceRead:
    company_repo = CompanyRepository(session)
    companies = await company_repo.get_by_ids([company_id])
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")
    company = companies[0]

    contact_repo = ContactRepository(session)
    intel = await contact_repo.get_company_intelligence(company_id)
    
    return CompanyIntelligenceRead(
        company_id=company.id,
        company_name=company.name,
        industry=None,
        contacts=[CompanyContactRead.model_validate(c) for c in intel["contacts"]],
        decision_makers=[DecisionMakerRead.model_validate(dm) for dm in intel["decision_makers"]],
    )


@router.get("", response_model=list[CompanyIntelligenceRead])
async def list_intelligence(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[CompanyIntelligenceRead]:
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(skip=skip, limit=limit)
    
    contact_repo = ContactRepository(session)
    
    results = []
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        if intel["contacts"] or intel["decision_makers"]:
            results.append(
                CompanyIntelligenceRead(
                    company_id=c.id,
                    company_name=c.name,
                    industry=None,
                    contacts=[CompanyContactRead.model_validate(co) for co in intel["contacts"]],
                    decision_makers=[DecisionMakerRead.model_validate(dm) for dm in intel["decision_makers"]],
                )
            )
    return results


@router.get("/export/excel")
async def export_intelligence_excel(
    session: AsyncSession = Depends(get_session),
) -> Any:
    from fastapi.responses import Response
    from leadminerai.services.export_service import ExportService

    contact_repo = ContactRepository(session)
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(limit=1000)
    
    contacts_list = []
    dms_list = []
    
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        for contact in intel["contacts"]:
            contacts_list.append({
                "company_name": c.name,
                "contact_type": contact.contact_type,
                "contact_value": contact.contact_value,
                "contact_label": contact.contact_label,
                "priority": contact.priority,
                "confidence": contact.confidence,
                "source_url": contact.source_url,
                "created_at": contact.created_at
            })
            
        for dm in intel["decision_makers"]:
            dms_list.append({
                "company_name": c.name,
                "name": dm.name,
                "designation": dm.designation,
                "linkedin_url": dm.linkedin_url,
                "priority": dm.priority,
                "confidence": dm.confidence,
                "source_url": dm.source_url,
                "created_at": dm.created_at
            })
            
    content = ExportService.build_intelligence_excel(contacts_list, dms_list)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="intelligence.xlsx"'},
    )


@router.get("/export/csv")
async def export_intelligence_csv(
    session: AsyncSession = Depends(get_session),
) -> Any:
    from fastapi.responses import Response
    from leadminerai.services.export_service import ExportService

    contact_repo = ContactRepository(session)
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(limit=1000)
    
    contacts_list = []
    dms_list = []
    
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        for contact in intel["contacts"]:
            contacts_list.append({
                "company_name": c.name,
                "contact_type": contact.contact_type,
                "contact_value": contact.contact_value,
                "contact_label": contact.contact_label,
                "priority": contact.priority,
                "confidence": contact.confidence,
                "source_url": contact.source_url,
                "created_at": contact.created_at
            })
            
        for dm in intel["decision_makers"]:
            dms_list.append({
                "company_name": c.name,
                "name": dm.name,
                "designation": dm.designation,
                "linkedin_url": dm.linkedin_url,
                "priority": dm.priority,
                "confidence": dm.confidence,
                "source_url": dm.source_url,
                "created_at": dm.created_at
            })
            
    content = ExportService.build_intelligence_csv(contacts_list, dms_list)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="intelligence.csv"'},
    )


@router.get("/export/json")
async def export_intelligence_json(
    session: AsyncSession = Depends(get_session),
) -> dict:
    import json
    contact_repo = ContactRepository(session)
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(limit=1000)
    
    results = {}
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        results[c.name] = {
            "website_url": c.website_url,
            "industry": None,
            "contacts": [
                {
                    "contact_type": contact.contact_type,
                    "contact_value": contact.contact_value,
                    "contact_label": contact.contact_label,
                    "priority": contact.priority,
                    "confidence": contact.confidence,
                    "source_url": contact.source_url
                }
                for contact in intel["contacts"]
            ],
            "decision_makers": [
                {
                    "name": dm.name,
                    "designation": dm.designation,
                    "linkedin_url": dm.linkedin_url,
                    "priority": dm.priority,
                    "confidence": dm.confidence,
                    "source_url": dm.source_url
                }
                for dm in intel["decision_makers"]
            ]
        }
    return results
