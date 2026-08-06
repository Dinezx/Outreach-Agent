from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from leadminerai.models.company import Company
from leadminerai.models.enums import CompanyStatus
from leadminerai.models.contact import CompanyContact
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_intelligence_api_endpoints(client: AsyncClient, test_app):
    sessionmaker = test_app.state.database.sessionmaker

    # Seed the database
    async with sessionmaker() as session:
        company = Company(
            id="comp-1",
            name="Alpha Corp",
            website_url="https://alphacorp.com",
            status=CompanyStatus.FOUND
        )
        session.add(company)
        await session.commit()

    # Test single extraction endpoint (mocking actual playwright and OpenAI calls)
    mock_extracted_data = {
        "contacts": [
            {
                "contact_type": "email",
                "contact_value": "purchase@alphacorp.com",
                "contact_label": "purchase@",
                "priority": 88,
                "source_url": "https://alphacorp.com/contact",
                "confidence": 98
            }
        ],
        "decision_makers": [
            {
                "name": "John Doe",
                "designation": "Operations Head",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "priority": 100,
                "source_url": "https://alphacorp.com/about",
                "confidence": 95
            }
        ]
    }

    with patch("leadminerai.services.crawler_service.CrawlerService.crawl", new_callable=AsyncMock) as mock_crawl, \
         patch("leadminerai.services.extractor_service.ExtractorService.extract", new_callable=AsyncMock) as mock_extract:
        
        mock_crawl.return_value = {"https://alphacorp.com": "<html></html>"}
        mock_extract.return_value = mock_extracted_data

        response = await client.post("/api/v1/intelligence/extract/comp-1")
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["intelligence"]["company_name"] == "Alpha Corp"
        assert len(res_json["intelligence"]["contacts"]) == 1
        assert res_json["intelligence"]["contacts"][0]["contact_value"] == "purchase@alphacorp.com"
        assert res_json["intelligence"]["contacts"][0]["priority"] == 88

    # Test GET list intelligence endpoint
    response = await client.get("/api/v1/intelligence")
    assert response.status_code == 200
    res_list = response.json()
    assert len(res_list) == 1
    assert res_list[0]["company_name"] == "Alpha Corp"
    assert res_list[0]["contacts"][0]["contact_value"] == "purchase@alphacorp.com"

    # Test GET single company intelligence endpoint
    response = await client.get("/api/v1/intelligence/comp-1")
    assert response.status_code == 200
    assert response.json()["company_name"] == "Alpha Corp"

    # Test GET export endpoints
    response = await client.get("/api/v1/intelligence/export/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    response = await client.get("/api/v1/intelligence/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

    response = await client.get("/api/v1/intelligence/export/json")
    assert response.status_code == 200
    assert "Alpha Corp" in response.json()

    # Test bulk extraction endpoint
    with patch("leadminerai.api.v1.intelligence.run_extract_all_background", new_callable=AsyncMock) as mock_bulk:
        response = await client.post("/api/v1/intelligence/extract-all")
        assert response.status_code == 200
        # Should return queued=0 because Alpha Corp already has intelligence in the DB
        assert response.json()["queued"] == 0
