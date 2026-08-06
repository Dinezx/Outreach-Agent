from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from leadminerai.api.deps import get_session
from leadminerai.core.config import Settings
from leadminerai.main import create_app
from leadminerai.models.base import Base


@pytest.fixture
async def test_app() -> AsyncIterator[FastAPI]:
    settings = Settings(
        app_name="LeadMinerAI",
        environment="test",
        database_url="sqlite+aiosqlite:///:memory:",
        tavily_api_key="test-key",
        tavily_base_url="https://api.tavily.com",
        tavily_search_depth="advanced",
        tavily_max_results=5,
        search_concurrency=2,
        log_level="INFO",
        log_serialize=False,
    )
    app = create_app(settings)
    engine = create_async_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_session():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    app.state.database.engine = engine
    app.state.database.sessionmaker = async_session
    try:
        yield app
    finally:
        await engine.dispose()


@pytest.fixture
async def client(test_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
