from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
import pytest


@pytest.mark.asyncio
async def test_upload_list_and_export(client):
    csv_content = b"company_name\nAcme Corp\nGlobex\n"
    response = await client.post(
        "/api/v1/companies/upload",
        files={"file": ("companies.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created"] == 2
    assert payload["skipped"] == 0

    list_response = await client.get("/api/v1/companies")
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2

    export_response = await client.get("/api/v1/companies/export")
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert len(export_response.content) > 0


@pytest.mark.asyncio
async def test_upload_xlsx(client):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["company_name"])
    worksheet.append(["Umbrella Corp"])
    buffer = BytesIO()
    workbook.save(buffer)

    response = await client.post(
        "/api/v1/companies/upload",
        files={"file": ("companies.xlsx", buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["created"] == 1
    assert payload["skipped"] == 0
