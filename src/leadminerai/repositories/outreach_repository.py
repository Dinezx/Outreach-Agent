from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leadminerai.models.outreach import OutreachCampaign, OutreachHistory
from leadminerai.models.enums import OutreachStatus


class OutreachRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_campaign(self, company_id: str, data: dict) -> OutreachCampaign:
        now = datetime.now(timezone.utc)
        campaign = OutreachCampaign(
            company_id=company_id,
            contact_id=data.get("contact_id"),
            decision_maker_id=data.get("decision_maker_id"),
            channel=data.get("channel", "office_email"),
            target_role=data.get("target_role"),
            subject=data.get("subject"),
            email_body=data.get("email_body"),
            linkedin_message=data.get("linkedin_message"),
            phone_script=data.get("phone_script"),
            recommendation_reason=data.get("recommendation_reason"),
            channel_confidence=data.get("channel_confidence", 0),
            overall_confidence=data.get("overall_confidence", 0),
            status=OutreachStatus.PENDING_APPROVAL,
            generation_time_ms=data.get("generation_time_ms", 0),
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            created_at=now,
            updated_at=now
        )
        self.session.add(campaign)
        await self.session.flush()

        history_item = OutreachHistory(
            campaign_id=campaign.id,
            action="GENERATED",
            notes=f"Outreach generated for target role: {data.get('target_role') or 'General Email'}",
            timestamp=now
        )
        self.session.add(history_item)

        await self.session.commit()
        return await self.get_by_id(campaign.id)  # type: ignore

    async def get_by_id(self, campaign_id: str) -> OutreachCampaign | None:
        stmt = (
            select(OutreachCampaign)
            .options(
                selectinload(OutreachCampaign.company),
                selectinload(OutreachCampaign.contact),
                selectinload(OutreachCampaign.decision_maker),
                selectinload(OutreachCampaign.history)
            )
            .where(OutreachCampaign.id == campaign_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_company_id(self, company_id: str) -> OutreachCampaign | None:
        stmt = (
            select(OutreachCampaign)
            .options(
                selectinload(OutreachCampaign.company),
                selectinload(OutreachCampaign.contact),
                selectinload(OutreachCampaign.decision_maker),
                selectinload(OutreachCampaign.history)
            )
            .where(OutreachCampaign.company_id == company_id)
            .order_by(OutreachCampaign.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_status(
        self,
        campaign_id: str,
        status: OutreachStatus,
        action: str,
        notes: str | None = None,
        rejection_reason: str | None = None,
        scheduled_at: datetime | None = None,
        sent_at: datetime | None = None
    ) -> OutreachCampaign:
        campaign = await self.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Outreach campaign {campaign_id} not found")

        now = datetime.now(timezone.utc)
        campaign.status = status
        campaign.updated_at = now

        if rejection_reason is not None:
            campaign.rejection_reason = rejection_reason
        if scheduled_at is not None:
            campaign.scheduled_at = scheduled_at
        if sent_at is not None:
            campaign.sent_at = sent_at

        history_item = OutreachHistory(
            campaign_id=campaign.id,
            action=action,
            notes=notes or f"Status changed to {status.value}",
            timestamp=now
        )
        self.session.add(history_item)

        await self.session.commit()
        self.session.expire_all()
        return await self.get_by_id(campaign_id)  # type: ignore

    async def update_content(
        self,
        campaign_id: str,
        subject: str | None = None,
        email_body: str | None = None,
        linkedin_message: str | None = None,
        phone_script: str | None = None,
        notes: str | None = None
    ) -> OutreachCampaign:
        campaign = await self.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Outreach campaign {campaign_id} not found")

        now = datetime.now(timezone.utc)
        if subject is not None:
            campaign.subject = subject
        if email_body is not None:
            campaign.email_body = email_body
        if linkedin_message is not None:
            campaign.linkedin_message = linkedin_message
        if phone_script is not None:
            campaign.phone_script = phone_script
        campaign.updated_at = now

        history_item = OutreachHistory(
            campaign_id=campaign.id,
            action="EDITED",
            notes=notes or "Campaign content edited by user",
            timestamp=now
        )
        self.session.add(history_item)

        await self.session.commit()
        self.session.expire_all()
        return await self.get_by_id(campaign_id)  # type: ignore



    async def list_campaigns(
        self,
        status: OutreachStatus | None = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[list[OutreachCampaign], int]:
        stmt = (
            select(OutreachCampaign)
            .options(
                selectinload(OutreachCampaign.company),
                selectinload(OutreachCampaign.contact),
                selectinload(OutreachCampaign.decision_maker),
                selectinload(OutreachCampaign.history)
            )
            .order_by(OutreachCampaign.updated_at.desc())
        )
        count_stmt = select(func.count()).select_from(OutreachCampaign)

        if status:
            stmt = stmt.where(OutreachCampaign.status == status)
            count_stmt = count_stmt.where(OutreachCampaign.status == status)

        total_res = await self.session.scalar(count_stmt)
        total = int(total_res or 0)

        res = await self.session.execute(stmt.offset(skip).limit(limit))
        items = list(res.scalars().all())
        return items, total
