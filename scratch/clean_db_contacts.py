import asyncio
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from sqlalchemy import select, delete
from leadminerai.models.contact import CompanyContact
from leadminerai.services.extractor_service import ExtractorService

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    
    deleted_count = 0
    updated_count = 0

    async with db.sessionmaker() as session:
        res = await session.execute(select(CompanyContact))
        contacts = res.scalars().all()
        print(f"Total contacts in database before cleanup: {len(contacts)}")
        
        for c in contacts:
            if c.contact_type == "phone":
                formatted, label = ExtractorService.clean_and_format_phone(c.contact_value)
                if not formatted:
                    print(f"[DELETE INVALID PHONE] ID: {c.id}, Val: '{c.contact_value}'")
                    await session.delete(c)
                    deleted_count += 1
                else:
                    if c.contact_value != formatted or c.contact_label != label:
                        print(f"[UPDATE PHONE] ID: {c.id}, Old: '{c.contact_value}' -> New: '{formatted}', Label: {label}")
                        c.contact_value = formatted
                        c.contact_label = label
                        updated_count += 1

            elif c.contact_type == "email":
                clean_email = ExtractorService.clean_and_format_email(c.contact_value)
                if not clean_email:
                    print(f"[DELETE INVALID EMAIL] ID: {c.id}, Val: '{c.contact_value}'")
                    await session.delete(c)
                    deleted_count += 1
                else:
                    if c.contact_value != clean_email:
                        print(f"[UPDATE EMAIL] ID: {c.id}, Old: '{c.contact_value}' -> New: '{clean_email}'")
                        c.contact_value = clean_email
                        updated_count += 1

        await session.commit()
        print(f"Cleanup finished! Deleted {deleted_count} invalid entries, updated {updated_count} entries.")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
