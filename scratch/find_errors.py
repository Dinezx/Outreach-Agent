import asyncio
from sqlalchemy import select
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.models.company import Company

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    async with db.sessionmaker() as session:
        res = await session.execute(select(Company))
        companies = res.scalars().all()
        print(f"Total companies: {len(companies)}")
        
        has_website = [c for c in companies if c.website_url is not None]
        print(f"Has website: {len(has_website)}")
        for c in has_website[:10]:
            print(f"- {c.name}: {c.website_url} (status: {c.status})")
            
        failed = [c for c in companies if c.last_error is not None]
        print(f"\nFailed companies with errors: {len(failed)}")
        for c in failed[:20]:
            print(f"- {c.name}: {c.last_error}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
