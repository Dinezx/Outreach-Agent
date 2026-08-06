from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from leadminerai.agents.tavily_agent import TavilySearchAgent
from leadminerai.core.config import Settings
from leadminerai.core.database import DatabaseManager
from leadminerai.services.company_service import CompanyService
from leadminerai.services.export_service import ExportService
from leadminerai.services.search_job_service import SearchJobService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_session(request: Request) -> AsyncSession:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    async with database.sessionmaker() as session:
        yield session


def get_company_service(session: AsyncSession = Depends(get_session)) -> CompanyService:
    return CompanyService(session)


def get_export_service() -> ExportService:
    return ExportService()


def get_tavily_agent(settings: Settings = Depends(get_settings)) -> TavilySearchAgent:
    return TavilySearchAgent(
        api_key=settings.tavily_api_key,
        base_url=settings.tavily_base_url,
        search_depth=settings.tavily_search_depth,
        max_results=settings.tavily_max_results,
        openai_api_key=settings.openai_api_key,
    )


def get_search_job_service(
    request: Request,
    settings: Settings = Depends(get_settings),
    agent: TavilySearchAgent = Depends(get_tavily_agent),
) -> SearchJobService:
    database: DatabaseManager = request.app.state.database
    if database.sessionmaker is None:
        raise RuntimeError("Database is not initialized")
    return SearchJobService(database.sessionmaker, agent, concurrency=settings.search_concurrency)
