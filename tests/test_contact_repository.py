from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from leadminerai.models.company import Company
from leadminerai.models.enums import CompanyStatus
from leadminerai.repositories.contact_repository import ContactRepository


@pytest.mark.asyncio
async def test_contact_repository_operations(test_app):
    sessionmaker = test_app.state.database.sessionmaker
    
    async with sessionmaker() as session:
        # Create a company first
        company1 = Company(
            id="company-1",
            name="Test Corp",
            website_url="https://testcorp.com",
            status=CompanyStatus.FOUND
        )
        company2 = Company(
            id="company-2",
            name="Another Corp",
            website_url="https://anothercorp.com",
            status=CompanyStatus.FOUND
        )
        session.add_all([company1, company2])
        await session.commit()

        repository = ContactRepository(session)
        
        # Test get_companies_without_contacts
        to_process = await repository.get_companies_without_contacts()
        assert len(to_process) == 2
        
        # Test upsert_contact_intelligence (insert)
        contacts_data = [
            {
                "contact_type": "email",
                "contact_value": "purchase@testcorp.com",
                "contact_label": "purchase@",
                "priority": 88,
                "confidence": 90,
                "source_url": "https://testcorp.com/contact"
            },
            {
                "contact_type": "phone",
                "contact_value": "+919444455555",
                "contact_label": "Mobile",
                "priority": 60,
                "confidence": 95,
                "source_url": "https://testcorp.com/contact"
            }
        ]
        decision_makers_data = [
            {
                "name": "Rajesh Kumar",
                "designation": "Operations Head",
                "linkedin_url": "https://linkedin.com/in/rajesh-kumar",
                "priority": 100,
                "confidence": 95,
                "source_url": "https://testcorp.com/about"
            }
        ]
        
        await repository.upsert_contact_intelligence("company-1", contacts_data, decision_makers_data)

        # Test get_companies_without_contacts again (should only have company2)
        to_process_2 = await repository.get_companies_without_contacts()
        assert len(to_process_2) == 1
        assert to_process_2[0].id == "company-2"

        # Test get_company_intelligence
        intel = await repository.get_company_intelligence("company-1")
        assert len(intel["contacts"]) == 2
        assert len(intel["decision_makers"]) == 1
        
        # Verify ordering (contacts sorted by priority desc)
        assert intel["contacts"][0].contact_value == "purchase@testcorp.com"
        assert intel["contacts"][1].contact_value == "+919444455555"
        assert intel["decision_makers"][0].name == "Rajesh Kumar"

        # Test upsert_contact_intelligence (update/re-import)
        updated_contacts = [
            {
                "contact_type": "email",
                "contact_value": "new@testcorp.com",
                "contact_label": "info@",
                "priority": 20,
                "confidence": 95,
                "source_url": "https://testcorp.com/contact"
            }
        ]
        await repository.upsert_contact_intelligence("company-1", updated_contacts, [])
        
        intel2 = await repository.get_company_intelligence("company-1")
        assert len(intel2["contacts"]) == 1
        assert intel2["contacts"][0].contact_value == "new@testcorp.com"
        assert len(intel2["decision_makers"]) == 0
