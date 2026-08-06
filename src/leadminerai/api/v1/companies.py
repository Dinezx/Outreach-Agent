from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from leadminerai.api.deps import get_company_service, get_export_service, get_search_job_service
from leadminerai.models.enums import CompanyStatus
from leadminerai.schemas.company import (
    CompanyListResponse,
    SearchTriggerRequest,
    SearchTriggerResponse,
    UploadResponse,
)
from leadminerai.services.company_service import CompanyService
from leadminerai.services.export_service import ExportService
from leadminerai.services.search_job_service import SearchJobService
from leadminerai.utils.csv_parser import parse_company_upload

from typing import Any

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_companies(file: UploadFile = File(...), service: CompanyService = Depends(get_company_service)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or XLSX uploads are supported")

    content = await file.read()
    try:
        names = parse_company_upload(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    created, skipped = await service.upload_companies(names)
    return UploadResponse(created=created, skipped=skipped, total_received=len(names))


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    status: CompanyStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    service: CompanyService = Depends(get_company_service),
) -> CompanyListResponse:
    items, total = await service.list_companies(status=status, skip=skip, limit=limit)
    return CompanyListResponse(items=items, total=total)


@router.post("/search/trigger", response_model=SearchTriggerResponse)
async def trigger_search(
    request: SearchTriggerRequest,
    background_tasks: BackgroundTasks,
    search_service: SearchJobService = Depends(get_search_job_service),
) -> SearchTriggerResponse:
    queued = await search_service.queued_count(request.company_ids)
    background_tasks.add_task(search_service.run, request.company_ids)
    return SearchTriggerResponse(queued=queued)


@router.get("/export")
async def export_companies(
    service: CompanyService = Depends(get_company_service),
    export_service: ExportService = Depends(get_export_service),
) -> Any:
    items, _ = await service.list_companies(limit=10_000)
    content = export_service.build_excel(items)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="companies.xlsx"'},
    )
