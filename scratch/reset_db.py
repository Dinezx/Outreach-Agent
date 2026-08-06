import asyncio
import sys
from pathlib import Path

# Add src folder to python path to run locally
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.models.company import Company
from leadminerai.models.contact import CompanyContact
from leadminerai.models.enums import CompanyStatus
from sqlalchemy import update, delete

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    
    async with db.sessionmaker() as session:
        async with session.begin():
            # Delete all contacts
            await session.execute(delete(CompanyContact))
            # Reset all companies to PENDING and website_url to None
            await session.execute(
                update(Company)
                .values(
                    status=CompanyStatus.PENDING,
                    website_url=None,
                    last_error=None
                )
            )
            print("Successfully deleted contacts and reset all companies to PENDING!")
            
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
