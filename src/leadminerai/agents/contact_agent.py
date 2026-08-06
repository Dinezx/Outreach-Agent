from __future__ import annotations

import time
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.extractor_service import ExtractorService
from leadminerai.repositories.contact_repository import ContactRepository
from loguru import logger


class ContactExtractionAgent:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        crawler_service: CrawlerService,
        extractor_service: ExtractorService
    ) -> None:
        self.sessionmaker = sessionmaker
        self.crawler_service = crawler_service
        self.extractor_service = extractor_service

    async def extract_contacts(self, company_id: str, company_name: str, website_url: str) -> dict:
        start_time = time.time()
        logger.info(f"ContactExtractionAgent: Processing {company_name} ({website_url})")

        try:
            crawled_pages = await self.crawler_service.crawl(website_url)
        except Exception as exc:
            logger.error(f"Crawl failed for {company_name}: {exc}")
            crawled_pages = {}

        extracted = await self.extractor_service.extract(crawled_pages, company_name)
        
        emails = ", ".join(extracted.get("emails", []))
        phones_list = extracted.get("phones", [])
        phone = phones_list[0] if len(phones_list) > 0 else None
        mobile = phones_list[1] if len(phones_list) > 1 else None

        db_data = {
            "email": emails if emails else None,
            "phone": phone,
            "mobile": mobile,
            "address": extracted.get("address") or None,
            "city": extracted.get("city") or None,
            "state": extracted.get("state") or None,
            "country": extracted.get("country") or None,
            "linkedin": extracted.get("linkedin") or None,
            "facebook": extracted.get("facebook") or None,
            "instagram": extracted.get("instagram") or None,
            "youtube": extracted.get("youtube") or None,
            "contact_page": extracted.get("contact_page") or None,
            "maps_url": extracted.get("maps_url") or None,
            "confidence_score": extracted.get("confidence", 0),
        }

        async with self.sessionmaker() as session:
            repository = ContactRepository(session)
            contact = await repository.upsert_contact(company_id, db_data)
            
        execution_time = time.time() - start_time
        logger.info(
            f"Extraction log:\n"
            f"Website: {website_url}\n"
            f"Pages crawled: {len(crawled_pages)}\n"
            f"Emails found: {emails}\n"
            f"Phones found: {', '.join(phones_list)}\n"
            f"Errors: None\n"
            f"Execution time: {execution_time:.2f}s"
        )
        return db_data
