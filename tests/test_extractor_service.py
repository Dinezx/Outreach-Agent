from __future__ import annotations

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from leadminerai.services.extractor_service import ExtractorService


def test_heuristic_extract():
    content = """
    Welcome to Test Corp.
    Email us at: purchase@testcorp.com or personal@gmail.com
    Call: +919444455555 or mobile +91-44-23456789
    Follow us: [Link: LinkedIn](https://linkedin.com/company/testcorp)
    Find us: [Link: Google Maps](https://google.com/maps/place/123+Street)
    """
    extractor = ExtractorService()
    result = extractor._heuristic_extract(content, "testcorp.com")
    
    contacts = result["contacts"]
    types = [c["contact_type"] for c in contacts]
    values = [c["contact_value"] for c in contacts]
    
    assert "email" in types
    assert "purchase@testcorp.com" in values
    # Should keep both corporate and personal if it can, but check domains
    assert "phone" in types
    assert "+919444455555" in [c["contact_value"].replace(" ", "") for c in contacts]
    assert "social" in types
    assert "https://linkedin.com/company/testcorp" in values
    assert "map" in types
    assert "https://google.com/maps/place/123+Street" in values


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_openai_extract_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "contacts": [
                            {
                                "contact_type": "email",
                                "contact_value": "purchase@testcorp.com",
                                "contact_label": "purchase@",
                                "source_url": "https://testcorp.com/contact",
                                "confidence": 95
                            }
                        ],
                        "decision_makers": [
                            {
                                "name": "Rajesh Kumar",
                                "designation": "Operations Head",
                                "linkedin_url": "https://linkedin.com/in/rajesh-kumar",
                                "source_url": "https://testcorp.com/about",
                                "confidence": 95
                            }
                        ]
                    })
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    extractor = ExtractorService(openai_api_key="mock-key")
    crawled_pages = {
        "https://testcorp.com": "<html><body>Contact purchase@testcorp.com</body></html>"
    }
    
    result = await extractor.extract(crawled_pages, "Test Corp")
    
    assert len(result["contacts"]) == 1
    assert result["contacts"][0]["contact_value"] == "purchase@testcorp.com"
    assert result["contacts"][0]["priority"] == 88  # purchase@ email priority
    
    assert len(result["decision_makers"]) == 1
    assert result["decision_makers"][0]["name"] == "Rajesh Kumar"
    assert result["decision_makers"][0]["priority"] == 100  # Operations Head priority
