from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_dashboard_renders(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "LeadMinerAI Dashboard" in response.text
    assert "Upload" in response.text
    assert "CSV" in response.text
