from leadminerai.utils.website_selection import SearchResult, select_official_website


def test_select_official_website_prefers_company_domain():
    results = [
        SearchResult(title="Acme on LinkedIn", url="https://www.linkedin.com/company/acme"),
        SearchResult(title="Acme Corp", url="https://acme.com", content="official website"),
    ]
    assert select_official_website("Acme Corp", results) == "https://acme.com"
