from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from leadminerai.models.contact import CompanyContact
from leadminerai.models.decision_maker import DecisionMaker
from leadminerai.models.company import Company
from leadminerai.models.enums import CompanyStatus


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_contacts_by_company_id(self, company_id: str) -> list[CompanyContact]:
        result = await self.session.execute(
            select(CompanyContact)
            .where(CompanyContact.company_id == company_id)
            .order_by(CompanyContact.priority.desc())
        )
        return list(result.scalars().all())

    async def get_decision_makers_by_company_id(self, company_id: str) -> list[DecisionMaker]:
        result = await self.session.execute(
            select(DecisionMaker)
            .where(DecisionMaker.company_id == company_id)
            .order_by(DecisionMaker.priority.desc())
        )
        return list(result.scalars().all())

    async def get_company_intelligence(self, company_id: str) -> dict:
        contacts = await self.get_contacts_by_company_id(company_id)
        decision_makers = await self.get_decision_makers_by_company_id(company_id)
        return {
            "contacts": contacts,
            "decision_makers": decision_makers
        }

    async def get_all_contacts(self, skip: int = 0, limit: int = 100) -> list[CompanyContact]:
        result = await self.session.execute(
            select(CompanyContact)
            .order_by(CompanyContact.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_decision_makers(self, skip: int = 0, limit: int = 100) -> list[DecisionMaker]:
        result = await self.session.execute(
            select(DecisionMaker)
            .order_by(DecisionMaker.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_all_contacts(self) -> int:
        return int(await self.session.scalar(select(func.count()).select_from(CompanyContact)) or 0)

    async def get_companies_without_contacts(self) -> list[Company]:
        subquery = select(CompanyContact.company_id).distinct()
        result = await self.session.execute(
            select(Company).where(
                Company.website_url.isnot(None),
                Company.status == CompanyStatus.FOUND,
                Company.id.not_in(subquery)
            )
        )
        return list(result.scalars().all())

    async def upsert_contact_intelligence(
        self,
        company_id: str,
        contacts_data: list[dict],
        decision_makers_data: list[dict]
    ) -> dict:
        # Delete existing contacts and decision makers
        await self.session.execute(delete(CompanyContact).where(CompanyContact.company_id == company_id))
        await self.session.execute(delete(DecisionMaker).where(DecisionMaker.company_id == company_id))

        # Add new contacts
        contacts = []
        for c in contacts_data:
            contact = CompanyContact(company_id=company_id, **c)
            self.session.add(contact)
            contacts.append(contact)

        # Add new decision makers
        decision_makers = []
        for dm in decision_makers_data:
            maker = DecisionMaker(company_id=company_id, **dm)
            self.session.add(maker)
            decision_makers.append(maker)

        await self.session.commit()
        return {
            "contacts": contacts,
            "decision_makers": decision_makers
        }

    # Compatibility methods
    async def get_by_company_id(self, company_id: str) -> CompanyContact | None:
        contacts = await self.get_contacts_by_company_id(company_id)
        return contacts[0] if contacts else None

    async def get_all_with_companies(self, skip: int = 0, limit: int = 100) -> list[tuple[CompanyContact, str]]:
        result = await self.session.execute(
            select(CompanyContact, Company.name)
            .join(Company, CompanyContact.company_id == Company.id)
            .order_by(CompanyContact.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())
