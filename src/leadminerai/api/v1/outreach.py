from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from leadminerai.api.deps import get_outreach_agent, get_session
from leadminerai.agents.outreach_intelligence_agent import OutreachIntelligenceAgent
from leadminerai.repositories.outreach_repository import OutreachRepository
from leadminerai.services.export_service import ExportService
from leadminerai.models.enums import OutreachStatus
from leadminerai.schemas.outreach import (
    OutreachApproveRequest,
    OutreachCampaignRead,
    OutreachEditRequest,
    OutreachGenerateAllResponse,
    OutreachGenerateResponse,
    OutreachListResponse,
    OutreachRejectRequest,
    OutreachScheduleRequest,
)

router = APIRouter(prefix="/outreach", tags=["Outreach Intelligence"])


def _to_campaign_read(c) -> OutreachCampaignRead:
    comp_name = c.company.name if c.company else None
    cont_val = c.contact.contact_value if c.contact else None
    dm_name = c.decision_maker.name if c.decision_maker else None
    dm_desig = c.decision_maker.designation if c.decision_maker else None

    return OutreachCampaignRead(
        id=c.id,
        company_id=c.company_id,
        company_name=comp_name,
        contact_id=c.contact_id,
        contact_value=cont_val,
        decision_maker_id=c.decision_maker_id,
        decision_maker_name=dm_name,
        decision_maker_designation=dm_desig,
        channel=c.channel,
        target_role=c.target_role,
        subject=c.subject,
        email_body=c.email_body,
        linkedin_message=c.linkedin_message,
        phone_script=c.phone_script,
        recommendation_reason=c.recommendation_reason,
        channel_confidence=c.channel_confidence,
        overall_confidence=c.overall_confidence,
        status=c.status,
        scheduled_at=c.scheduled_at,
        sent_at=c.sent_at,
        rejection_reason=c.rejection_reason,
        generation_time_ms=c.generation_time_ms,
        prompt_tokens=c.prompt_tokens,
        completion_tokens=c.completion_tokens,
        history=c.history or [],
        created_at=c.created_at,
        updated_at=c.updated_at
    )


@router.post("/generate/{company_id}", response_model=OutreachGenerateResponse)
async def generate_outreach(
    company_id: str,
    agent: OutreachIntelligenceAgent = Depends(get_outreach_agent)
) -> OutreachGenerateResponse:
    try:
        campaign = await agent.generate_campaign(company_id)
        return OutreachGenerateResponse(
            success=True,
            message="Successfully generated outreach intelligence campaign",
            campaign=_to_campaign_read(campaign)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate outreach: {str(exc)}"
        )


@router.post("/generate-all", response_model=OutreachGenerateAllResponse)
async def generate_all_outreach(
    background_tasks: BackgroundTasks,
    agent: OutreachIntelligenceAgent = Depends(get_outreach_agent)
) -> OutreachGenerateAllResponse:
    background_tasks.add_task(agent.generate_all_campaigns)
    return OutreachGenerateAllResponse(
        queued=1,
        message="Queued bulk outreach intelligence generation in the background."
    )


@router.get("", response_model=OutreachListResponse)
@router.get("/", response_model=OutreachListResponse)
async def list_outreach_campaigns(
    status_filter: OutreachStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session)
) -> OutreachListResponse:
    repo = OutreachRepository(session)
    items, total = await repo.list_campaigns(status=status_filter, skip=skip, limit=limit)
    return OutreachListResponse(
        total=total,
        items=[_to_campaign_read(c) for c in items]
    )


@router.get("/{campaign_id}", response_model=OutreachCampaignRead)
async def get_outreach_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.get_by_id(campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Outreach campaign not found")
    return _to_campaign_read(c)


@router.put("/{campaign_id}/approve", response_model=OutreachCampaignRead)
async def approve_outreach_campaign(
    campaign_id: str,
    body: OutreachApproveRequest = OutreachApproveRequest(),
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.update_status(
        campaign_id=campaign_id,
        status=OutreachStatus.APPROVED,
        action="APPROVED",
        notes=body.notes or "Campaign manually approved by human operator"
    )
    return _to_campaign_read(c)


@router.put("/{campaign_id}/reject", response_model=OutreachCampaignRead)
async def reject_outreach_campaign(
    campaign_id: str,
    body: OutreachRejectRequest = OutreachRejectRequest(),
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.update_status(
        campaign_id=campaign_id,
        status=OutreachStatus.REJECTED,
        action="REJECTED",
        rejection_reason=body.reason or "Campaign rejected during human review",
        notes=body.reason or "Campaign rejected"
    )
    return _to_campaign_read(c)


@router.put("/{campaign_id}/edit", response_model=OutreachCampaignRead)
async def edit_outreach_campaign(
    campaign_id: str,
    body: OutreachEditRequest,
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.update_content(
        campaign_id=campaign_id,
        subject=body.subject,
        email_body=body.email_body,
        linkedin_message=body.linkedin_message,
        phone_script=body.phone_script,
        notes="Edited outreach content"
    )
    return _to_campaign_read(c)


@router.post("/{campaign_id}/schedule", response_model=OutreachCampaignRead)
async def schedule_outreach_campaign(
    campaign_id: str,
    body: OutreachScheduleRequest,
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.update_status(
        campaign_id=campaign_id,
        status=OutreachStatus.SCHEDULED,
        action="SCHEDULED",
        scheduled_at=body.scheduled_at,
        notes=f"Scheduled for {body.scheduled_at.isoformat()}"
    )
    return _to_campaign_read(c)


@router.post("/{campaign_id}/send", response_model=OutreachCampaignRead)
async def send_outreach_campaign(
    campaign_id: str,
    session: AsyncSession = Depends(get_session)
) -> OutreachCampaignRead:
    repo = OutreachRepository(session)
    c = await repo.get_by_id(campaign_id)
    if not c:
        raise HTTPException(status_code=404, detail="Outreach campaign not found")

    if c.status not in (OutreachStatus.APPROVED, OutreachStatus.SCHEDULED, OutreachStatus.PENDING_APPROVAL):
        raise HTTPException(status_code=400, detail=f"Cannot send campaign in status {c.status}")

    now = datetime.now(timezone.utc)
    updated = await repo.update_status(
        campaign_id=campaign_id,
        status=OutreachStatus.SENT,
        action="SENT",
        sent_at=now,
        notes="Outreach invitation dispatched successfully"
    )
    return _to_campaign_read(updated)


@router.get("/export/csv")
async def export_outreach_csv(
    status_filter: OutreachStatus | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_session)
) -> Response:
    repo = OutreachRepository(session)
    items, _ = await repo.list_campaigns(status=status_filter, limit=5000)
    data = [_to_campaign_read(c).model_dump() for c in items]
    content = ExportService.build_outreach_csv(data)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=outreach_campaigns.csv"}
    )


@router.get("/export/excel")
async def export_outreach_excel(
    status_filter: OutreachStatus | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_session)
) -> Response:
    repo = OutreachRepository(session)
    items, _ = await repo.list_campaigns(status=status_filter, limit=5000)
    data = [_to_campaign_read(c).model_dump() for c in items]
    content = ExportService.build_outreach_excel(data)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=outreach_campaigns.xlsx"}
    )


@router.get("/export/pdf")
async def export_outreach_pdf(
    status_filter: OutreachStatus | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_session)
) -> Response:
    repo = OutreachRepository(session)
    items, _ = await repo.list_campaigns(status=status_filter, limit=5000)
    data = [_to_campaign_read(c).model_dump() for c in items]
    content = ExportService.build_outreach_pdf(data)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=outreach_briefs.pdf"}
    )
