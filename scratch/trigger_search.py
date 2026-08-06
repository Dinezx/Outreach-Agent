import asyncio
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.agents.tavily_agent import TavilySearchAgent
from leadminerai.services.search_job_service import SearchJobService
from sqlalchemy import select, update
from leadminerai.models.company import Company
from leadminerai.models.enums import CompanyStatus

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    
    agent = TavilySearchAgent(
        api_key=settings.tavily_api_key,
        base_url=settings.tavily_base_url,
        search_depth=settings.tavily_search_depth,
        max_results=settings.tavily_max_results,
        openai_api_key=settings.openai_api_key
    )
    
    service = SearchJobService(db.sessionmaker, agent, concurrency=5)
    
    # Mark all FAILED companies back to PENDING first so that run() picks them up
    async with db.sessionmaker() as session:
        await session.execute(
            update(Company)
            .where(Company.status == CompanyStatus.FAILED)
            .values(status=CompanyStatus.PENDING)
        )
        await session.commit()
        print("Reset all FAILED companies to PENDING.")
        
    print("Running website search...")
    queued = await service.queued_count()
    print("Queued count:", queued)
    
    processed = await service.run()
    print(f"Processed {processed} companies.")
    
    # Check results
    async with db.sessionmaker() as session:
        res = await session.execute(select(Company))
        companies = res.scalars().all()
        found = [c for c in companies if c.status == CompanyStatus.FOUND]
        failed = [c for c in companies if c.status == CompanyStatus.FAILED]
        pending = [c for c in companies if c.status == CompanyStatus.PENDING]
        print(f"Results: FOUND={len(found)}, FAILED={len(failed)}, PENDING={len(pending)}")
        for c in found[:10]:
            print(f"- {c.name}: {c.website_url}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
