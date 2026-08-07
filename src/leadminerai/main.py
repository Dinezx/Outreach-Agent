from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from leadminerai.api.v1.router import api_router
from leadminerai.api.v1.contact import router as contact_router
from leadminerai.core.config import Settings, get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.core.logging import setup_logging
from leadminerai.models.base import Base
from leadminerai.web.dashboard import get_dashboard_html


def create_app(settings: Settings | None = None) -> FastAPI:
    app_title = settings.app_name if settings else "LeadMinerAI"
    app = FastAPI(title=app_title, version="0.1.0")
    app.state.settings = settings
    app.state.database = DatabaseManager(settings.database_url) if settings else None

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        resolved_settings = app.state.settings or get_settings()
        app.state.settings = resolved_settings
        setup_logging(resolved_settings)
        if app.state.database is None:
            app.state.database = DatabaseManager(resolved_settings.database_url)
        await app.state.database.connect()
        if resolved_settings.database_url.startswith("sqlite") and app.state.database.engine is not None:
            async with app.state.database.engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
        else:
            try:
                import subprocess
                import sys
                from loguru import logger
                subprocess.run(
                    [sys.executable, "-m", "alembic", "upgrade", "head"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info("Alembic migrations applied programmatically on startup via subprocess")
            except Exception as exc:
                from loguru import logger
                logger.error(f"Failed to run programmatic migrations: {exc}")
        try:
            yield
        finally:
            await app.state.database.disconnect()

    app.router.lifespan_context = lifespan

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(contact_router, prefix="/api/contact")
    
    from leadminerai.api.v1.business_intelligence import router as business_intel_router
    app.include_router(business_intel_router, prefix="/api/intelligence", tags=["business-intelligence-alias"])

    from leadminerai.api.v1.outreach import router as outreach_alias_router
    app.include_router(outreach_alias_router, prefix="/api", tags=["outreach-alias"])

    from leadminerai.api.v1.gmail import router as gmail_alias_router
    app.include_router(gmail_alias_router, prefix="/api", tags=["gmail-alias"])




    @app.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        return get_dashboard_html()

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def run() -> None:
    uvicorn.run("leadminerai.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
