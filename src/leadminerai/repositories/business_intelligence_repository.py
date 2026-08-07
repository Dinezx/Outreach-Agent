from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leadminerai.models.business_intelligence import CompanyBusinessIntelligence
from leadminerai.models.company import Company


class BusinessIntelligenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_business_intelligence(
        self,
        company_id: str,
        data: dict
    ) -> CompanyBusinessIntelligence:
        # Check if record exists
        stmt = select(CompanyBusinessIntelligence).where(CompanyBusinessIntelligence.company_id == company_id)
        res = await self.session.execute(stmt)
        record = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)

        if record:
            record.industry = data.get("industry")
            record.sub_industry = data.get("sub_industry")
            record.description = data.get("description")
            record.products = data.get("products", [])
            record.services = data.get("services", [])
            record.manufacturing_type = data.get("manufacturing_type")
            record.departments = data.get("departments", [])
            record.locations = data.get("locations", [])
            record.certifications = data.get("certifications", [])
            record.markets = data.get("markets", [])
            record.keywords = data.get("keywords", [])
            record.pain_points = data.get("pain_points", [])
            record.confidence = data.get("confidence", 0)
            record.updated_at = now
        else:
            record = CompanyBusinessIntelligence(
                company_id=company_id,
                industry=data.get("industry"),
                sub_industry=data.get("sub_industry"),
                description=data.get("description"),
                products=data.get("products", []),
                services=data.get("services", []),
                manufacturing_type=data.get("manufacturing_type"),
                departments=data.get("departments", []),
                locations=data.get("locations", []),
                certifications=data.get("certifications", []),
                markets=data.get("markets", []),
                keywords=data.get("keywords", []),
                pain_points=data.get("pain_points", []),
                confidence=data.get("confidence", 0),
                created_at=now,
                updated_at=now
            )
            self.session.add(record)

        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_by_company_id(self, company_id: str) -> CompanyBusinessIntelligence | None:
        stmt = (
            select(CompanyBusinessIntelligence)
            .options(selectinload(CompanyBusinessIntelligence.company))
            .where(CompanyBusinessIntelligence.company_id == company_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_intelligence(
        self,
        industry: str | None = None,
        city: str | None = None,
        manufacturing_type: str | None = None,
        predicted_pain: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[CompanyBusinessIntelligence], int]:
        stmt = (
            select(CompanyBusinessIntelligence)
            .join(Company, CompanyBusinessIntelligence.company_id == Company.id)
            .options(selectinload(CompanyBusinessIntelligence.company))
            .order_by(CompanyBusinessIntelligence.updated_at.desc())
        )
        count_stmt = (
            select(func.count())
            .select_from(CompanyBusinessIntelligence)
            .join(Company, CompanyBusinessIntelligence.company_id == Company.id)
        )

        if industry:
            pattern = f"%{industry}%"
            stmt = stmt.where(CompanyBusinessIntelligence.industry.ilike(pattern))
            count_stmt = count_stmt.where(CompanyBusinessIntelligence.industry.ilike(pattern))

        if manufacturing_type:
            pattern = f"%{manufacturing_type}%"
            stmt = stmt.where(CompanyBusinessIntelligence.manufacturing_type.ilike(pattern))
            count_stmt = count_stmt.where(CompanyBusinessIntelligence.manufacturing_type.ilike(pattern))

        res = await self.session.execute(stmt)
        all_records = list(res.scalars().all())

        # Post-filter for JSON arrays (city locations & predicted_pain) to ensure compatibility across all SQL engines
        filtered = []
        for record in all_records:
            keep = True
            if city:
                city_lower = city.lower()
                locations_text = " ".join([str(l).lower() for l in (record.locations or [])])
                if city_lower not in locations_text and city_lower not in (record.description or "").lower():
                    keep = False

            if keep and predicted_pain:
                pain_lower = predicted_pain.lower()
                pains_text = " ".join([
                    f"{p.get('name', '')} {p.get('frequency', '')}"
                    for p in (record.pain_points or [])
                    if isinstance(p, dict)
                ]).lower()
                if pain_lower not in pains_text:
                    keep = False

            if keep:
                filtered.append(record)

        total = len(filtered)
        paginated = filtered[skip : skip + limit]
        return paginated, total

    async def get_all_companies(self) -> list[Company]:
        stmt = select(Company).where(Company.website_url.is_not(None))
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

