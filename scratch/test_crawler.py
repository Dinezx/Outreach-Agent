import asyncio
from leadminerai.services.crawler_service import CrawlerService

async def main():
    crawler = CrawlerService()
    try:
        pages = await crawler.crawl("https://example.com")
        print("Success! Crawled pages:", len(pages))
    except Exception as e:
        print("Error encountered:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
