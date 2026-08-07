import asyncio
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from sqlalchemy import select
from leadminerai.models.contact import CompanyContact
from leadminerai.models.company import Company

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    
    async with db.sessionmaker() as session:
        # Get all contacts
        res = await session.execute(select(CompanyContact))
        contacts = res.scalars().all()
        print(f"Total contacts: {len(contacts)}")
        for c in contacts:
            if c.contact_type == "phone":
                print(f"ID: {c.id}, Company ID: {c.company_id}, Type: {c.contact_type}, Value: {c.contact_value}, Label: {c.contact_label}, Confidence: {c.confidence}")
                
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
