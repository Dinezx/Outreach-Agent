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


def test_clean_and_format_phone():
    # Invalid numbers that should return None
    invalid_numbers = [
        "32 36 58 14 44",
        "36 35 32 40 29",
        "30 33 33 35 41",
        "23 24 23 27 26",
        "28 29 29 30 30",
        "34 40 61 20 55",
        "24 19 48 11 41",
        "46 61.76 10.32",
        "22.90 18.07 44",
        "2023-2030",
        "9001-2015",
        "9001 2105",
        "2447 2143",
        "1234567890",
    ]
    for num in invalid_numbers:
        formatted, _ = ExtractorService.clean_and_format_phone(num)
        assert formatted is None, f"Expected None for invalid phone '{num}', got '{formatted}'"

    # Valid numbers that should format correctly
    valid_map = {
        "+91 9454551851": ("+91 94545 51851", "Mobile"),
        "044-25340523": ("044-25340523", "Office"),
        "0422-2223512": ("0422-2223512", "Office"),
        "7756979228": ("+91 77569 79228", "Mobile"),
        "1800 123 4567": ("1800-123-4567", "Toll-Free"),
    }
    for num, expected in valid_map.items():
        formatted, label = ExtractorService.clean_and_format_phone(num)
        assert formatted == expected[0], f"Expected {expected[0]} for '{num}', got '{formatted}'"
        assert label == expected[1]

