from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from leadminerai.agents.tavily_agent import TavilySearchAgent


@pytest.mark.asyncio
async def test_tavily_agent_fallback_on_replace_me():
    agent = TavilySearchAgent(
        api_key="replace-me",
        base_url="https://api.tavily.com",
        search_depth="advanced",
        max_results=5,
    )
    url = await agent.find_official_website("ELGi Equipments")
    assert url == "https://www.elgi.com"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_tavily_agent_fallback_on_401_unauthorized(mock_post):
    mock_post.side_effect = Exception("401 Unauthorized")
    agent = TavilySearchAgent(
        api_key="invalid-key",
        base_url="https://api.tavily.com",
        search_depth="advanced",
        max_results=5,
    )
    url = await agent.find_official_website("Pricol Ltd")
    assert url == "https://www.pricol.com"
