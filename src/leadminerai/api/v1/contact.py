from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
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
    ContactRead,
    ContactDetailedRead,
)
from leadminerai.repositories.contact_repository import ContactRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.extractor_service import ExtractorService
from leadminerai.services.export_service import ExportService
from leadminerai.agents.contact_intelligence_agent import ContactIntelligenceAgent

router = APIRouter()


def get_intelligence_agent(request: Request, settings: Settings = Depends(get_settings)) -> ContactIntelligenceAgent:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    crawler = CrawlerService()
    extractor = ExtractorService(settings.openai_api_key)
    return ContactIntelligenceAgent(database.sessionmaker, crawler, extractor)


def _map_to_legacy_contact(company_id: str, intel: dict) -> dict:
    contacts = intel.get("contacts") or []
    flat = {
        "id": company_id,
        "company_id": company_id,
        "email": None,
        "phone": None,
        "mobile": None,
        "address": None,
        "city": None,
        "state": None,
        "country": None,
        "linkedin": None,
        "facebook": None,
        "instagram": None,
        "youtube": None,
        "contact_page": None,
        "maps_url": None,
        "confidence_score": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    emails = []
    phones = []
    mobiles = []
    
    for c in contacts:
        ctype = c.contact_type
        cval = c.contact_value
        clabel = c.contact_label
        
        if c.confidence > flat["confidence_score"]:
            flat["confidence_score"] = c.confidence
            
        if ctype == "email":
            emails.append(cval)
        elif ctype == "phone":
            if "mobile" in clabel.lower():
                mobiles.append(cval)
            else:
                phones.append(cval)
        elif ctype == "address":
            flat["address"] = cval
        elif ctype == "social":
            if "linkedin" in clabel.lower() or "linkedin" in cval:
                flat["linkedin"] = cval
            elif "facebook" in clabel.lower() or "facebook" in cval:
                flat["facebook"] = cval
            elif "instagram" in clabel.lower() or "instagram" in cval:
                flat["instagram"] = cval
            elif "youtube" in clabel.lower() or "youtube" in cval:
                flat["youtube"] = cval
        elif ctype == "map":
            flat["maps_url"] = cval
            
        flat["created_at"] = c.created_at
        flat["updated_at"] = c.updated_at
        
    if emails:
        flat["email"] = ", ".join(emails)
    if phones:
        flat["phone"] = phones[0]
    if mobiles:
        flat["mobile"] = mobiles[0]
        
    return flat


@router.post("/extract", response_model=ContactExtractResponse)
async def extract_contact(
    payload: ContactExtractRequest,
    session: AsyncSession = Depends(get_session),
    agent: ContactIntelligenceAgent = Depends(get_intelligence_agent),
) -> ContactExtractResponse:
    company_repo = CompanyRepository(session)
    companies = await company_repo.get_by_ids([payload.company_id])
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
        
        contact_repo = ContactRepository(session)
        intel = await contact_repo.get_company_intelligence(company.id)
        
        legacy_data = _map_to_legacy_contact(company.id, intel)
        
        return ContactExtractResponse(
            success=True,
            message="Contacts extracted successfully",
            contact=ContactRead.model_validate(legacy_data)
        )
    except Exception as exc:
        logger.error(f"Contact extraction failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


async def run_extract_all_background(database_sessionmaker, settings: Settings):
    logger.info("Starting background bulk contact extraction task")
    crawler = CrawlerService()
    extractor = ExtractorService(settings.openai_api_key)
    agent = ContactIntelligenceAgent(database_sessionmaker, crawler, extractor)

    async with database_sessionmaker() as session:
        contact_repo = ContactRepository(session)
        companies = await contact_repo.get_companies_without_contacts()

    logger.info(f"Bulk extraction task queued {len(companies)} companies")
    for company in companies:
        if company.website_url:
            try:
                await agent.extract_intelligence(company.id, company.name, company.website_url)
            except Exception as exc:
                logger.error(f"Background extraction failed for company {company.name}: {exc}")
            await asyncio.sleep(0.5)


@router.post("/extract-all", response_model=ContactExtractAllResponse)
async def extract_all_contacts(
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
            message="No companies found matching the criteria (has website, but contacts empty)"
        )

    background_tasks.add_task(run_extract_all_background, database.sessionmaker, settings)
    return ContactExtractAllResponse(
        queued=len(companies),
        message=f"Queued background contact extraction for {len(companies)} companies"
    )


@router.get("", response_model=list[ContactDetailedRead])
async def list_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[ContactDetailedRead]:
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(skip=skip, limit=limit)
    
    contact_repo = ContactRepository(session)
    results = []
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        if intel["contacts"]:
            legacy_data = _map_to_legacy_contact(c.id, intel)
            legacy_data["company_name"] = c.name
            results.append(ContactDetailedRead.model_validate(legacy_data))
    return results


@router.get("/export/excel")
async def export_contacts_excel(
    session: AsyncSession = Depends(get_session),
) -> Any:
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(limit=10000)
    
    contact_repo = ContactRepository(session)
    data = []
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        if intel["contacts"]:
            legacy_data = _map_to_legacy_contact(c.id, intel)
            legacy_data["company_name"] = c.name
            data.append(legacy_data)
    
    content = ExportService.build_contacts_excel(data)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="contacts.xlsx"'},
    )


@router.get("/export/csv")
async def export_contacts_csv(
    session: AsyncSession = Depends(get_session),
) -> Any:
    company_repo = CompanyRepository(session)
    companies, _ = await company_repo.list_companies(limit=10000)
    
    contact_repo = ContactRepository(session)
    data = []
    for c in companies:
        intel = await contact_repo.get_company_intelligence(c.id)
        if intel["contacts"]:
            legacy_data = _map_to_legacy_contact(c.id, intel)
            legacy_data["company_name"] = c.name
            data.append(legacy_data)
    
    content = ExportService.build_contacts_csv(data)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="contacts.csv"'},
    )


@router.get("/{company_id}", response_model=ContactRead)
async def get_company_contacts(
    company_id: str,
    session: AsyncSession = Depends(get_session),
) -> ContactRead:
    company_repo = CompanyRepository(session)
    companies = await company_repo.get_by_ids([company_id])
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")
    
    contact_repo = ContactRepository(session)
    intel = await contact_repo.get_company_intelligence(company_id)
    if not intel["contacts"]:
        raise HTTPException(status_code=404, detail="Contacts not found for this company")
        
    legacy_data = _map_to_legacy_contact(company_id, intel)
    return ContactRead.model_validate(legacy_data)
