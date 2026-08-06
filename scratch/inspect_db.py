import asyncio
from sqlalchemy import select
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.models.company import Company
from leadminerai.models.contact import CompanyContact
from leadminerai.models.decision_maker import DecisionMaker
from leadminerai.models.enums import CompanyStatus

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    async with db.sessionmaker() as session:
        # Get FOUND companies
        res = await session.execute(select(Company).where(Company.status == CompanyStatus.FOUND))
        companies = res.scalars().all()
        print(f"Total FOUND companies in database: {len(companies)}")
        for comp in companies:
            print(f"- Company: {comp.name}, URL: {comp.website_url}")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
