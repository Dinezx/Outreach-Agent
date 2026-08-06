from __future__ import annotations

import asyncio
import urllib.robotparser
from urllib.parse import urljoin, urlparse
import httpx
from playwright.async_api import async_playwright
from leadminerai.services.html_service import HTMLService
from loguru import logger

SKIP_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".zip", ".tar", ".gz",
    ".mp4", ".avi", ".mov", ".mp3", ".wav", ".exe", ".dmg", ".bin"
}


class RobotsTxtChecker:
    def __init__(self, base_url: str) -> None:
        self.parser = urllib.robotparser.RobotFileParser()
        parsed = urlparse(base_url)
        self.robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        self.loaded = False

    async def load(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(self.robots_url)
                if response.status_code == 200:
                    self.parser.parse(response.text.splitlines())
                    self.loaded = True
        except Exception:
            pass

    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        if not self.loaded:
            return True
        try:
            return self.parser.can_fetch(user_agent, url)
        except Exception:
            return True


class CrawlerService:
    def __init__(self, timeout_ms: int = 15000, max_pages: int = 10, concurrency: int = 3) -> None:
        self.timeout_ms = timeout_ms
        self.max_pages = max_pages
        self.concurrency = concurrency

    def _is_same_domain(self, url: str, base_url: str) -> bool:
        try:
            url_netloc = urlparse(url).netloc.lower()
            base_netloc = urlparse(base_url).netloc.lower()
            return url_netloc.replace("www.", "") == base_netloc.replace("www.", "")
        except Exception:
            return False

    def _should_skip(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return any(path.endswith(ext) for ext in SKIP_EXTENSIONS)

    def _score_url(self, url: str) -> int:
        path = urlparse(url).path.lower()
        score = 0
        keywords = {
            "contact": 10,
            "about": 9,
            "team": 8,
            "leader": 8,
            "management": 8,
            "people": 8,
            "board": 8,
            "career": 7,
            "job": 7,
            "location": 7,
            "branch": 7,
            "office": 7,
            "dealer": 6,
            "distributor": 6,
            "corporate": 5,
            "privacy": 4,
            "terms": 3,
        }
        for kw, val in keywords.items():
            if kw in path:
                score += val
        return score

    async def crawl(self, start_url: str) -> dict[str, str]:
        logger.info(f"Starting crawl for website: {start_url}")
        
        checker = RobotsTxtChecker(start_url)
        await checker.load()

        if not checker.can_fetch(start_url):
            logger.warning(f"Crawl disallowed by robots.txt for: {start_url}")
            return {}

        crawled_pages: dict[str, str] = {}
        to_crawl: list[tuple[int, str]] = [(100, start_url)]
        visited = {start_url}

        async_playwright_ctx = async_playwright()
        playwright = await async_playwright_ctx.__aenter__()
        try:
            browser = await playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) LeadMinerAICrawler/1.0",
                viewport={"width": 1280, "height": 800}
            )

            async def crawl_page(url: str) -> str | None:
                if not checker.can_fetch(url):
                    logger.info(f"Skipping page due to robots.txt: {url}")
                    return None
                
                retries = 2
                for attempt in range(retries):
                    page = await context.new_page()
                    try:
                        logger.info(f"Crawling {url} (attempt {attempt + 1})")
                        response = await page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
                        if response and response.status >= 400:
                            logger.warning(f"Failed to load page {url}: HTTP {response.status}")
                            await page.close()
                            return None
                        
                        html = await page.content()
                        await page.close()
                        return html
                    except Exception as exc:
                        logger.error(f"Error crawling {url} on attempt {attempt + 1}: {exc}")
                        await page.close()
                        if attempt == retries - 1:
                            return None
                        await asyncio.sleep(1.0)
                return None

            # Crawl homepage first
            homepage_html = await crawl_page(start_url)
            if not homepage_html:
                logger.error(f"Failed to crawl homepage: {start_url}")
                await browser.close()
                await async_playwright_ctx.__aexit__(None, None, None)
                return {}

            crawled_pages[start_url] = homepage_html

            # Extract links from homepage
            all_links = HTMLService.extract_links(homepage_html, start_url)
            for link in all_links:
                if link not in visited and self._is_same_domain(link, start_url) and not self._should_skip(link):
                    score = self._score_url(link)
                    if score > 0:
                        to_crawl.append((score, link))
                        visited.add(link)

            # Sort queue by priority (score) descending
            to_crawl.sort(key=lambda x: x[0], reverse=True)
            links_to_crawl = [item[1] for item in to_crawl if item[1] != start_url][:self.max_pages - 1]

            semaphore = asyncio.Semaphore(self.concurrency)

            async def worker(url: str):
                async with semaphore:
                    # Delay for rate limiting
                    await asyncio.sleep(0.5)
                    html = await crawl_page(url)
                    if html:
                        crawled_pages[url] = html

            await asyncio.gather(*(worker(url) for url in links_to_crawl))
            await browser.close()
        finally:
            await async_playwright_ctx.__aexit__(None, None, None)

        logger.info(f"Crawl completed for {start_url}. Crawled {len(crawled_pages)} pages.")
        return crawled_pages
