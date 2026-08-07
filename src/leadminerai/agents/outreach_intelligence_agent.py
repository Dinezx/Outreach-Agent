from __future__ import annotations

import time
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from leadminerai.services.outreach_generator_service import OutreachGeneratorService
from leadminerai.repositories.outreach_repository import OutreachRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.repositories.contact_repository import ContactRepository
from leadminerai.repositories.business_intelligence_repository import BusinessIntelligenceRepository
from leadminerai.models.outreach import OutreachCampaign


class OutreachIntelligenceAgent:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        outreach_generator_service: OutreachGeneratorService
    ) -> None:
        self.sessionmaker = sessionmaker
        self.outreach_generator_service = outreach_generator_service

    async def generate_campaign(self, company_id: str) -> OutreachCampaign:
        start_time = time.time()

        async with self.sessionmaker() as session:
            company_repo = CompanyRepository(session)
            companies = await company_repo.get_by_ids([company_id])
            if not companies:
                raise ValueError(f"Company ID {company_id} not found")
            company = companies[0]

            contact_repo = ContactRepository(session)
            intel = await contact_repo.get_company_intelligence(company_id)
            contacts_list = [
                {
                    "id": c.id,
                    "contact_type": c.contact_type,
                    "contact_value": c.contact_value,
                    "contact_label": c.contact_label,
                    "priority": c.priority,
                    "confidence": c.confidence
                }
                for c in intel.get("contacts", [])
            ]
            dms_list = [
                {
                    "id": dm.id,
                    "name": dm.name,
                    "designation": dm.designation,
                    "linkedin_url": dm.linkedin_url,
                    "priority": dm.priority,
                    "confidence": dm.confidence
                }
                for dm in intel.get("decision_makers", [])
            ]

            bi_repo = BusinessIntelligenceRepository(session)
            bi_record = await bi_repo.get_by_company_id(company_id)
            company_intel = {}
            if bi_record:
                company_intel = {
                    "industry": bi_record.industry,
                    "sub_industry": bi_record.sub_industry,
                    "description": bi_record.description,
                    "products": bi_record.products or [],
                    "services": bi_record.services or [],
                    "manufacturing_type": bi_record.manufacturing_type,
                    "locations": bi_record.locations or [],
                    "certifications": bi_record.certifications or [],
                    "pain_points": bi_record.pain_points or []
                }

        logger.info(f"OutreachIntelligenceAgent: Generating campaign for {company.name} ({company_id})")

        generated = await self.outreach_generator_service.generate_outreach(
            company_name=company.name,
            company_intel=company_intel,
            contacts=contacts_list,
            decision_makers=dms_list,
            website_url=company.website_url
        )

        contact_id = None
        decision_maker_id = None
        target_contact = generated.get("contact")
        if target_contact:
            decision_maker_id = target_contact.get("id")

        campaign_data = {
            "contact_id": contact_id,
            "decision_maker_id": decision_maker_id,
            "channel": generated.get("channel", "office_email"),
            "target_role": generated.get("target_role"),
            "subject": generated.get("subject"),
            "email_body": generated.get("email_body"),
            "linkedin_message": generated.get("linkedin_message"),
            "phone_script": generated.get("phone_script"),
            "recommendation_reason": generated.get("recommendation_reason"),
            "channel_confidence": generated.get("channel_confidence", 0),
            "overall_confidence": generated.get("overall_confidence", 0),
            "generation_time_ms": generated.get("generation_time_ms", 0),
            "prompt_tokens": generated.get("prompt_tokens", 0),
            "completion_tokens": generated.get("completion_tokens", 0),
        }

        async with self.sessionmaker() as session:
            outreach_repo = OutreachRepository(session)

            # Check if campaign already exists for company
            existing = await outreach_repo.get_by_company_id(company_id)
            if existing:
                # Update content and reset to PENDING_APPROVAL
                await outreach_repo.update_content(
                    existing.id,
                    subject=generated.get("subject"),
                    email_body=generated.get("email_body"),
                    linkedin_message=generated.get("linkedin_message"),
                    phone_script=generated.get("phone_script"),
                    notes="Regenerated campaign via Outreach Intelligence Agent"
                )
                campaign = await outreach_repo.get_by_id(existing.id)
            else:
                campaign = await outreach_repo.create_campaign(company_id, campaign_data)

        exec_time = time.time() - start_time
        logger.info(
            f"=== Outreach Generation Log ===\n"
            f"Company: {company.name}\n"
            f"Target Role: {generated.get('target_role')}\n"
            f"Recommended Channel: {generated.get('channel')} ({generated.get('channel_confidence')}%\n"
            f"Overall Confidence: {generated.get('overall_confidence')}%\n"
            f"Prompt Tokens: {generated.get('prompt_tokens')}\n"
            f"Completion Tokens: {generated.get('completion_tokens')}\n"
            f"Generation Time: {exec_time:.2f}s ({generated.get('generation_time_ms')}ms)\n"
            f"==============================="
        )

        return campaign

    async def generate_all_campaigns(self) -> int:
        logger.info("OutreachIntelligenceAgent: Starting batch outreach generation for all companies")
        companies = []
        async with self.sessionmaker() as session:
            company_repo = CompanyRepository(session)
            companies, _ = await company_repo.list_companies(limit=1000)

        count = 0
        for company in companies:
            try:
                await self.generate_campaign(company.id)
                count += 1
            except Exception as exc:
                logger.error(f"Batch outreach generation failed for {company.name} ({company.id}): {exc}")

        logger.info(f"OutreachIntelligenceAgent: Batch generation complete. Created/updated {count} campaigns.")
        return count
