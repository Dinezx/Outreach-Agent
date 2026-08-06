from __future__ import annotations

import time
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.extractor_service import ExtractorService
from leadminerai.repositories.contact_repository import ContactRepository
from loguru import logger


class ContactIntelligenceAgent:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        crawler_service: CrawlerService,
        extractor_service: ExtractorService
    ) -> None:
        self.sessionmaker = sessionmaker
        self.crawler_service = crawler_service
        self.extractor_service = extractor_service

    async def extract_intelligence(self, company_id: str, company_name: str, website_url: str) -> dict:
        start_time = time.time()
        logger.info(f"ContactIntelligenceAgent: Initiating extraction for {company_name} ({website_url})")

        retries = 3
        crawled_pages = {}
        error_msg = None
        
        for attempt in range(retries):
            try:
                crawled_pages = await self.crawler_service.crawl(website_url)
                if crawled_pages:
                    error_msg = None
                    break
                else:
                    error_msg = "No pages crawled"
            except Exception as exc:
                error_msg = str(exc)
                logger.warning(f"Crawling attempt {attempt + 1} failed for {company_name}: {exc}")
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(1.0)

        # Even if crawl failed or empty, try extraction to let fallback/heuristics or DB update happen safely
        extracted = {}
        try:
            extracted = await self.extractor_service.extract(crawled_pages, company_name)
        except Exception as exc:
            error_msg = f"Extraction failed: {exc}"
            logger.error(error_msg)
            extracted = {"contacts": [], "decision_makers": []}

        contacts_data = extracted.get("contacts") or []
        decision_makers_data = extracted.get("decision_makers") or []

        # Save to database using the repository
        async with self.sessionmaker() as session:
            repository = ContactRepository(session)
            await repository.upsert_contact_intelligence(company_id, contacts_data, decision_makers_data)

        execution_time = time.time() - start_time
        logger.info(
            f"Extraction Log Summary:\n"
            f"Website: {website_url}\n"
            f"Pages Crawled: {len(crawled_pages)}\n"
            f"Contacts Found: {len(contacts_data)}\n"
            f"Decision Makers Found: {len(decision_makers_data)}\n"
            f"Execution Time: {execution_time:.2f}s\n"
            f"Errors: {error_msg or 'None'}"
        )

        return {
            "contacts": contacts_data,
            "decision_makers": decision_makers_data,
            "execution_time": execution_time,
            "pages_crawled": len(crawled_pages),
            "error": error_msg
        }
