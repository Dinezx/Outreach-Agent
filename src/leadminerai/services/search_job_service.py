from __future__ import annotations

import asyncio
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from leadminerai.agents.tavily_agent import TavilySearchAgent
from leadminerai.models.enums import CompanyStatus
from leadminerai.repositories.company_repository import CompanyRepository


class SearchJobService:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession], agent: TavilySearchAgent, concurrency: int = 5) -> None:
        self.sessionmaker = sessionmaker
        self.agent = agent
        self.concurrency = max(1, concurrency)

    async def queued_count(self, company_ids: Sequence[str] | None = None) -> int:
        async with self.sessionmaker() as session:
            repository = CompanyRepository(session)
            if company_ids:
                return await repository.count_by_ids(company_ids)
            return await repository.count_pending()

    async def run(self, company_ids: Sequence[str] | None = None) -> int:
        async with self.sessionmaker() as session:
            repository = CompanyRepository(session)
            if company_ids:
                companies = await repository.get_by_ids(company_ids)
            else:
                companies = await repository.get_pending()

        semaphore = asyncio.Semaphore(self.concurrency)

        async def process(company) -> None:
            async with semaphore:
                async with self.sessionmaker() as session:
                    repo = CompanyRepository(session)
                    try:
                        website_url = await self.agent.find_official_website(company.name)
                        if website_url:
                            await repo.update_search_result(
                                company.id,
                                status=CompanyStatus.FOUND,
                                website_url=website_url,
                                last_error=None,
                            )
                        else:
                            await repo.update_search_result(
                                company.id,
                                status=CompanyStatus.NOT_FOUND,
                                website_url=None,
                                last_error=None,
                            )
                    except Exception as exc:  # pragma: no cover - defensive logging boundary
                        await repo.update_search_result(
                            company.id,
                            status=CompanyStatus.FAILED,
                            website_url=None,
                            last_error=str(exc),
                        )

        await asyncio.gather(*(process(company) for company in companies))
        return len(companies)
