import asyncio
from leadminerai.core.config import get_settings
from leadminerai.core.database import DatabaseManager
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.extractor_service import ExtractorService
from leadminerai.agents.contact_intelligence_agent import ContactIntelligenceAgent
from sqlalchemy import select
from leadminerai.models.company import Company
from leadminerai.models.contact import CompanyContact
from leadminerai.models.decision_maker import DecisionMaker

async def main():
    settings = get_settings()
    db = DatabaseManager(settings.database_url)
    await db.connect()
    
    crawler = CrawlerService(concurrency=2)
    extractor = ExtractorService(openai_api_key=settings.openai_api_key)
    agent = ContactIntelligenceAgent(db.sessionmaker, crawler, extractor)
    
    # Get a company to extract
    async with db.sessionmaker() as session:
        res = await session.execute(
            select(Company).where(Company.name == "Suguna Pumps")
        )
        company = res.scalar_one_or_none()
        if not company:
            print("Company 'Suguna Pumps' not found!")
            await db.disconnect()
            return
        
        company_id = company.id
        company_name = company.name
        website_url = company.website_url
        print(f"Target company: {company_name}, website: {website_url}")

    print("Extracting intelligence...")
    result = await agent.extract_intelligence(company_id, company_name, website_url)
    print("\n--- Extraction Results ---")
    print("Contacts Found:", len(result["contacts"]))
    for c in result["contacts"]:
        print(f"- {c['contact_type']}: {c['contact_value']} (prio: {c['priority']}, conf: {c['confidence']})")
        
    print("\nDecision Makers Found:", len(result["decision_makers"]))
    for dm in result["decision_makers"]:
        print(f"- {dm['name']} ({dm['designation']}) (prio: {dm['priority']})")
        
    print("Error:", result["error"])
    
    # Check DB
    async with db.sessionmaker() as session:
        res = await session.execute(
            select(CompanyContact).where(CompanyContact.company_id == company_id)
        )
        contacts = res.scalars().all()
        print("\nStored Contacts in DB:", len(contacts))
        
        res = await session.execute(
            select(DecisionMaker).where(DecisionMaker.company_id == company_id)
        )
        dms = res.scalars().all()
        print("Stored DMs in DB:", len(dms))

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
