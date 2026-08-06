from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from leadminerai.models.enums import CompanyStatus
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.schemas.company import CompanyRead


class CompanyService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = CompanyRepository(session)

    async def upload_companies(self, names: list[str]) -> tuple[int, int]:
        return await self.repository.add_companies(names)

    async def list_companies(
        self,
        status: CompanyStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[CompanyRead], int]:
        rows, total = await self.repository.list_companies(status=status, skip=skip, limit=limit)
        return [CompanyRead.model_validate(row) for row in rows], total
