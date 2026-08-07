from __future__ import annotations

import pytest
from httpx import AsyncClient
from leadminerai.services.business_extractor_service import BusinessExtractorService
from leadminerai.repositories.business_intelligence_repository import BusinessIntelligenceRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.models.enums import CompanyStatus


@pytest.mark.asyncio
async def test_business_extractor_service_heuristic():
    extractor = BusinessExtractorService(openai_api_key=None)
    pages = {
        "https://examplepump.com": "<html><body><h1>Apex Pumps Pvt Ltd</h1><p>We are a leading manufacturer of submersible pumps, industrial valves, and CNC machined components in Coimbatore. Certified ISO 9001:2015 and CE Mark. We export to Middle East and Europe.</p></body></html>"
    }

    result = await extractor.extract_business_intelligence(pages, "Apex Pumps Pvt Ltd")
    assert result["industry"] in ["Flow Control & Pumps", "Precision Engineering", "Industrial Manufacturing"]
    assert "submersible pumps" in " ".join(result["products"]).lower() or "pump" in result["sub_industry"].lower()
    assert any("ISO" in c for c in result["certifications"])
    assert len(result["departments"]) > 0
    assert len(result["pain_points"]) > 0
    assert result["confidence"] > 50


@pytest.mark.asyncio
async def test_business_intelligence_repository(test_app):
    sessionmaker = test_app.state.database.sessionmaker

    async with sessionmaker() as session:
        company_repo = CompanyRepository(session)
        await company_repo.add_companies(["Texmo Industries"])
        companies = await company_repo.get_pending()
        company_id = companies[0].id

        bi_repo = BusinessIntelligenceRepository(session)
        data = {
            "industry": "Flow Control & Pumps",
            "sub_industry": "Submersible Pumps",
            "description": "Texmo Industries manufactures high efficiency motors and pumps.",
            "products": ["Taro Submersible Pump", "Monoblock Pump"],
            "services": ["Custom Assembly"],
            "manufacturing_type": "OEM",
            "departments": [{"name": "Production", "confidence": 95}],
            "locations": ["Coimbatore, Tamil Nadu"],
            "certifications": ["ISO 9001:2015"],
            "markets": ["India"],
            "keywords": ["pumps", "motors"],
            "pain_points": [{"name": "Production Delays", "severity": 85, "frequency": "Daily", "confidence": 90}],
            "confidence": 92
        }

        record = await bi_repo.upsert_business_intelligence(company_id, data)
        assert record.company_id == company_id
        assert record.industry == "Flow Control & Pumps"

        fetched = await bi_repo.get_by_company_id(company_id)
        assert fetched is not None
        assert fetched.manufacturing_type == "OEM"

        items, total = await bi_repo.list_intelligence(industry="Pumps")
        assert total == 1
        assert len(items) == 1


@pytest.mark.asyncio
async def test_business_intelligence_api_endpoints(client: AsyncClient, test_app):
    sessionmaker = test_app.state.database.sessionmaker

    # Add company with website URL
    async with sessionmaker() as session:
        company_repo = CompanyRepository(session)
        await company_repo.add_companies(["L&T Valves"])
        companies = await company_repo.get_pending()
        company = companies[0]
        await company_repo.update_search_result(company.id, CompanyStatus.FOUND, website_url="https://ltvalves.com")

    # Call single company business analysis endpoint
    resp = await client.post(f"/api/intelligence/analyze/{company.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["intelligence"]["company_id"] == company.id
    assert data["intelligence"]["industry"] is not None

    # Call get intelligence endpoint
    get_resp = await client.get(f"/api/intelligence/{company.id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["company_id"] == company.id

    # Call list endpoint
    list_resp = await client.get("/api/v1/business-intelligence")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1

    # Call exports
    csv_resp = await client.get("/api/v1/business-intelligence/export/csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]

    excel_resp = await client.get("/api/v1/business-intelligence/export/excel")
    assert excel_resp.status_code == 200
    assert "spreadsheetml" in excel_resp.headers["content-type"]

    json_resp = await client.get("/api/v1/business-intelligence/export/json")
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers["content-type"]
