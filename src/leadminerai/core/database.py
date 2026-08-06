from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class DatabaseManager:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine: AsyncEngine | None = None
        self.sessionmaker: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        if self.engine is not None:
            return
        self.engine = create_async_engine(self.database_url, pool_pre_ping=True)
        self.sessionmaker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.sessionmaker = None
