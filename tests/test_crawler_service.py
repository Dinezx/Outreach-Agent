from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from leadminerai.services.crawler_service import CrawlerService, RobotsTxtChecker


@pytest.mark.asyncio
async def test_robots_txt_checker_allows_by_default():
    checker = RobotsTxtChecker("https://example.com")
    # Even if load fails, it should default to allow
    assert checker.can_fetch("https://example.com/contact") is True


@pytest.mark.asyncio
@patch("leadminerai.services.crawler_service.async_playwright")
async def test_crawler_service_success(mock_playwright):
    # Mock playwright instance
    mock_play = AsyncMock()
    mock_playwright.return_value = mock_play
    mock_play.__aenter__.return_value = mock_play
    
    mock_browser = AsyncMock()
    mock_play.chromium.launch.return_value = mock_browser
    
    mock_context = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    
    mock_page1 = AsyncMock()
    mock_page2 = AsyncMock()
    mock_context.new_page.side_effect = [mock_page1, mock_page2]
    
    # Homepage mock response
    mock_response1 = MagicMock()
    mock_response1.status = 200
    mock_page1.goto.return_value = mock_response1
    mock_page1.content.return_value = """
    <html>
      <body>
        <a href="/contact">Contact Page</a>
        <a href="/external">External</a>
      </body>
    </html>
    """
    
    # Contact page mock response
    mock_response2 = MagicMock()
    mock_response2.status = 200
    mock_page2.goto.return_value = mock_response2
    mock_page2.content.return_value = "<html><body>Email: info@example.com</body></html>"
    
    crawler = CrawlerService(max_pages=2)
    with patch("leadminerai.services.crawler_service.RobotsTxtChecker.load", new_callable=AsyncMock):
        results = await crawler.crawl("https://example.com")
        
    assert "https://example.com" in results
    assert "https://example.com/contact" in results
    assert "info@example.com" in results["https://example.com/contact"]
