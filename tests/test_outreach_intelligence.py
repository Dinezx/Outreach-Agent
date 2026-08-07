from __future__ import annotations

import pytest
from httpx import AsyncClient

from leadminerai.services.outreach_generator_service import OutreachGeneratorService
from leadminerai.repositories.outreach_repository import OutreachRepository
from leadminerai.repositories.company_repository import CompanyRepository
from leadminerai.repositories.contact_repository import ContactRepository
from leadminerai.models.enums import CompanyStatus, OutreachStatus


@pytest.mark.asyncio
async def test_contact_channel_evaluation():
    service = OutreachGeneratorService(openai_api_key=None)

    contacts = [{"contact_type": "email", "contact_value": "info@texmopumps.com"}]
    decision_makers = [
        {"name": "Suresh Kumar", "designation": "Plant Head & Operations Manager", "linkedin_url": "https://linkedin.com/in/suresh"},
        {"name": "Ramesh V", "designation": "Sales Executive"}
    ]

    best_dm, target_role, best_channel, channel_conf, reason = service.evaluate_contacts_and_channels(
        contacts, decision_makers, company_website="https://texmopumps.com"
    )

    assert best_dm["name"] == "Suresh Kumar"
    assert "Operations Manager" in target_role or "Plant Head" in target_role
    assert best_channel == "office_email"
    assert channel_conf >= 90
    assert "production" in reason.lower() or "operations" in reason.lower()


@pytest.mark.asyncio
async def test_outreach_generator_service_heuristic():
    service = OutreachGeneratorService(openai_api_key=None)

    company_intel = {
        "industry": "Flow Control & Pumps",
        "products": ["Submersible Pump", "Monoblock Motor"],
        "manufacturing_type": "OEM",
        "locations": ["Coimbatore, Tamil Nadu"]
    }
    contacts = [{"contact_type": "email", "contact_value": "contact@apexvalves.com"}]
    decision_makers = [{"name": "Karthik Raja", "designation": "Operations Lead"}]

    result = await service.generate_outreach(
        company_name="Apex Valves Ltd",
        company_intel=company_intel,
        contacts=contacts,
        decision_makers=decision_makers,
        website_url="https://apexvalves.com"
    )

    assert result["subject"] is not None
    assert "research" in result["email_body"].lower() or "study" in result["email_body"].lower()

    # Verify Email word count constraint <= 180 words
    email_words = result["email_body"].split()
    assert len(email_words) <= 180

    # Verify LinkedIn message length <= 300 chars
    assert len(result["linkedin_message"]) <= 300

    # Verify Phone script format
    assert "Dinesh Kumar" in result["phone_script"]
    assert "not selling" in result["phone_script"].lower()
    assert result["overall_confidence"] >= 70


@pytest.mark.asyncio
async def test_outreach_repository(test_app):
    sessionmaker = test_app.state.database.sessionmaker

    async with sessionmaker() as session:
        company_repo = CompanyRepository(session)
        await company_repo.add_companies(["TVS Motors"])
        companies = await company_repo.get_pending()
        company_id = companies[0].id

        outreach_repo = OutreachRepository(session)
        campaign_data = {
            "channel": "office_email",
            "target_role": "Plant Operations Head",
            "subject": "Research Invitation: Operations Benchmarking",
            "email_body": "Dear Plant Operations Head, ...",
            "linkedin_message": "Hello, conducting research study...",
            "phone_script": "Hello, Dinesh Kumar here...",
            "recommendation_reason": "Selected Plant Operations Head",
            "channel_confidence": 95,
            "overall_confidence": 90,
            "generation_time_ms": 120,
            "prompt_tokens": 150,
            "completion_tokens": 100
        }

        campaign = await outreach_repo.create_campaign(company_id, campaign_data)
        assert campaign.company_id == company_id
        assert campaign.status == OutreachStatus.PENDING_APPROVAL
        assert len(campaign.history) == 1
        assert campaign.history[0].action == "GENERATED"

        # Update content
        updated = await outreach_repo.update_content(
            campaign.id,
            subject="Updated Research Subject",
            notes="Edited subject line"
        )
        assert updated.subject == "Updated Research Subject"
        assert len(updated.history) == 2

        # Approve
        approved = await outreach_repo.update_status(
            campaign.id,
            status=OutreachStatus.APPROVED,
            action="APPROVED",
            notes="Manually approved"
        )
        assert approved.status == OutreachStatus.APPROVED
        assert len(approved.history) == 3


@pytest.mark.asyncio
async def test_outreach_api_endpoints(client: AsyncClient, test_app):
    sessionmaker = test_app.state.database.sessionmaker

    # Create test company with contacts
    async with sessionmaker() as session:
        company_repo = CompanyRepository(session)
        await company_repo.add_companies(["Roots Industries"])
        companies = await company_repo.get_pending()
        company = companies[0]
        await company_repo.update_search_result(company.id, CompanyStatus.FOUND, website_url="https://roots.co.in")

        contact_repo = ContactRepository(session)
        await contact_repo.upsert_contact_intelligence(
            company.id,
            [{"contact_type": "email", "contact_value": "info@roots.co.in", "contact_label": "Office Email", "priority": 10, "confidence": 90}],
            [{"name": "R. Varadarajan", "designation": "Operations Director", "priority": 10, "confidence": 90}]
        )



    # Generate outreach via API
    gen_resp = await client.post(f"/api/outreach/generate/{company.id}")
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["success"] is True
    campaign_id = gen_data["campaign"]["id"]
    assert gen_data["campaign"]["status"] == "PENDING_APPROVAL"

    # List outreach campaigns
    list_resp = await client.get("/api/outreach")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1

    # Get campaign details
    detail_resp = await client.get(f"/api/outreach/{campaign_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == campaign_id

    # Edit campaign
    edit_resp = await client.put(f"/api/outreach/{campaign_id}/edit", json={
        "subject": "Edited Research Invitation Subject"
    })
    assert edit_resp.status_code == 200
    assert edit_resp.json()["subject"] == "Edited Research Invitation Subject"

    # Approve campaign
    approve_resp = await client.put(f"/api/outreach/{campaign_id}/approve", json={"notes": "Approved for research"})
    assert approve_resp.status_code == 200
    assert approve_resp.json()["status"] == "APPROVED"

    # Send campaign
    send_resp = await client.post(f"/api/outreach/{campaign_id}/send")
    assert send_resp.status_code == 200
    assert send_resp.json()["status"] == "SENT"

    # Test Exports
    csv_resp = await client.get("/api/outreach/export/csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]

    excel_resp = await client.get("/api/outreach/export/excel")
    assert excel_resp.status_code == 200
    assert "spreadsheetml" in excel_resp.headers["content-type"]

    pdf_resp = await client.get("/api/outreach/export/pdf")
    assert pdf_resp.status_code == 200
    assert "application/pdf" in pdf_resp.headers["content-type"]
