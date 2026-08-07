from __future__ import annotations

import asyncio
import time
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from leadminerai.services.crawler_service import CrawlerService
from leadminerai.services.business_extractor_service import BusinessExtractorService
from leadminerai.repositories.business_intelligence_repository import BusinessIntelligenceRepository
from leadminerai.repositories.company_repository import CompanyRepository


class CompanyBusinessIntelligenceAgent:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        crawler_service: CrawlerService,
        business_extractor_service: BusinessExtractorService
    ) -> None:
        self.sessionmaker = sessionmaker
        self.crawler_service = crawler_service
        self.business_extractor_service = business_extractor_service

    async def analyze_company(self, company_id: str) -> dict:
        start_time = time.time()

        # Fetch company details
        company_name = ""
        website_url = ""
        async with self.sessionmaker() as session:
            repo = CompanyRepository(session)
            companies = await repo.get_by_ids([company_id])
            if not companies:
                raise ValueError(f"Company ID {company_id} not found")
            company = companies[0]
            company_name = company.name
            website_url = company.website_url or ""

        logger.info(f"CompanyBusinessIntelligenceAgent: Starting business analysis for {company_name} ({website_url})")

        crawled_pages = {}
        error_msg = None

        if website_url:
            retries = 3
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
                        await asyncio.sleep(1.0)

        # Extract business intelligence (uses fallback if empty/failed)
        extracted = await self.business_extractor_service.extract_business_intelligence(
            crawled_pages, company_name
        )

        pages_crawled_count = len(crawled_pages)
        products_found_count = len(extracted.get("products", []))
        departments_predicted_count = len(extracted.get("departments", []))
        pain_points_generated_count = len(extracted.get("pain_points", []))

        # Save to database using BusinessIntelligenceRepository
        async with self.sessionmaker() as session:
            repository = BusinessIntelligenceRepository(session)
            record = await repository.upsert_business_intelligence(company_id, extracted)

        execution_time = time.time() - start_time

        # Structured Logging as required in specification
        logger.info(
            f"=== Business Intelligence Analysis Log ===\n"
            f"Company: {company_name} (ID: {company_id})\n"
            f"Pages Crawled: {pages_crawled_count}\n"
            f"Products Found: {products_found_count}\n"
            f"Departments Predicted: {departments_predicted_count}\n"
            f"Pain Points Generated: {pain_points_generated_count}\n"
            f"Execution Time: {execution_time:.2f}s\n"
            f"Status: {'Success' if not error_msg else 'Warnings: ' + error_msg}\n"
            f"=========================================="
        )

        return {
            "company_id": company_id,
            "company_name": company_name,
            "intelligence": extracted,
            "pages_crawled": pages_crawled_count,
            "products_found": products_found_count,
            "departments_predicted": departments_predicted_count,
            "pain_points_generated": pain_points_generated_count,
            "execution_time": execution_time,
            "error": error_msg
        }

    async def analyze_all_companies(self) -> int:
        logger.info("CompanyBusinessIntelligenceAgent: Starting batch business intelligence analysis for all companies.")
        companies = []
        async with self.sessionmaker() as session:
            repo = BusinessIntelligenceRepository(session)
            companies = await repo.get_all_companies()

        count = 0
        for company in companies:
            try:
                await self.analyze_company(company.id)
                count += 1
            except Exception as exc:
                logger.error(f"Batch analysis failed for company {company.name} ({company.id}): {exc}")

        logger.info(f"CompanyBusinessIntelligenceAgent: Completed batch analysis for {count} companies.")
        return count
