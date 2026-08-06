from io import BytesIO

from openpyxl import Workbook

from leadminerai.utils.csv_parser import parse_company_csv
from leadminerai.utils.csv_parser import parse_company_upload
from leadminerai.utils.csv_parser import parse_company_xlsx


def test_parse_company_csv_accepts_company_name_column():
    names = parse_company_csv(b"company_name\nAcme\nGlobex\n")
    assert names == ["Acme", "Globex"]


def test_parse_company_csv_requires_known_column():
    try:
        parse_company_csv(b"foo\nbar\n")
    except ValueError as exc:
        assert "company_name" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_parse_company_xlsx_accepts_company_name_column():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["company_name"])
    worksheet.append(["Acme"])
    worksheet.append(["Globex"])
    buffer = BytesIO()
    workbook.save(buffer)

    names = parse_company_xlsx(buffer.getvalue())
    assert names == ["Acme", "Globex"]


def test_parse_company_upload_detects_xlsx():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["name"])
    worksheet.append(["Initech"])
    buffer = BytesIO()
    workbook.save(buffer)

    names = parse_company_upload("companies.xlsx", buffer.getvalue())
    assert names == ["Initech"]
