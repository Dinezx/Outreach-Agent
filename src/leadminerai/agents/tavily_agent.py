from __future__ import annotations

from dataclasses import dataclass

import httpx

from leadminerai.agents.openai_ranker import choose_official_website_with_openai
from leadminerai.utils.website_selection import SearchResult, select_official_website


@dataclass(slots=True)
class TavilySearchAgent:
    api_key: str
    base_url: str
    search_depth: str
    max_results: int
    openai_api_key: str | None = None

    async def find_official_website(self, company_name: str) -> str | None:
        if not self.api_key or self.api_key == "replace-me":
            return self._heuristic_website_guess(company_name)

        payload = {
            "api_key": self.api_key,
            "query": f"{company_name} India official website",
            "search_depth": self.search_depth,
            "max_results": self.max_results,
            "include_answer": False,
            "include_raw_content": False,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.base_url.rstrip('/')}/search", json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return self._heuristic_website_guess(company_name)

        raw_results = data.get("results", [])
        results = [
            SearchResult(title=item.get("title", ""), url=item.get("url", ""), content=item.get("content"))
            for item in raw_results
            if item.get("url")
        ]

        if self.openai_api_key:
            try:
                selected_url = await choose_official_website_with_openai(self.openai_api_key, company_name, results)
                if selected_url:
                    return selected_url
            except Exception:  # pragma: no cover - optional enrichment path
                pass

        return select_official_website(company_name, results)

    def _heuristic_website_guess(self, company_name: str) -> str:
        import re
        clean = company_name.lower()
        clean = re.sub(r'\b(ltd|limited|pvt|private|corp|corporation|inc|incorporated|co|company|group|pumps|equipments|india)\b', '', clean)
        clean = re.sub(r'[^a-z0-9]', '', clean)
        if not clean:
            clean = "example"
        return f"https://www.{clean}.com"
