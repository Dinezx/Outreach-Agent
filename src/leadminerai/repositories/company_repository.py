from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from leadminerai.models.company import Company
from leadminerai.models.enums import CompanyStatus


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_companies(self, names: Sequence[str]) -> tuple[int, int]:
        normalized = []
        seen = set()
        for name in names:
            cleaned = name.strip() if name else ""
            if cleaned and cleaned not in seen:
                normalized.append(cleaned)
                seen.add(cleaned)
        if not normalized:
            return 0, 0

        existing_result = await self.session.execute(select(Company.name).where(Company.name.in_(normalized)))
        existing_names = set(existing_result.scalars().all())

        to_create = [Company(name=name, status=CompanyStatus.PENDING) for name in normalized if name not in existing_names]
        if to_create:
            self.session.add_all(to_create)
            await self.session.commit()

        return len(to_create), len(normalized) - len(to_create)

    async def count_pending(self) -> int:
        return int(await self.session.scalar(select(func.count()).select_from(Company).where(Company.status == CompanyStatus.PENDING)) or 0)

    async def count_by_ids(self, company_ids: Sequence[str]) -> int:
        if not company_ids:
            return 0
        return int(await self.session.scalar(select(func.count()).select_from(Company).where(Company.id.in_(company_ids))) or 0)

    async def list_companies(
        self,
        status: CompanyStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Company], int]:
        query = select(Company).order_by(Company.created_at.desc())
        count_query = select(func.count()).select_from(Company)
        if status is not None:
            query = query.where(Company.status == status)
            count_query = count_query.where(Company.status == status)

        total = await self.session.scalar(count_query)
        result = await self.session.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all()), int(total or 0)

    async def get_by_ids(self, company_ids: Sequence[str]) -> list[Company]:
        if not company_ids:
            return []
        result = await self.session.execute(select(Company).where(Company.id.in_(company_ids)))
        return list(result.scalars().all())

    async def get_pending(self) -> list[Company]:
        result = await self.session.execute(select(Company).where(Company.status == CompanyStatus.PENDING))
        return list(result.scalars().all())

    async def update_search_result(
        self,
        company_id: str,
        status: CompanyStatus,
        website_url: str | None = None,
        last_error: str | None = None,
    ) -> None:
        stmt = (
            update(Company)
            .where(Company.id == company_id)
            .values(
                status=status,
                website_url=website_url,
                last_error=last_error,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
