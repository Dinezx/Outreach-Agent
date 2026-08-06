from __future__ import annotations

import json

import httpx

from leadminerai.utils.website_selection import SearchResult


async def choose_official_website_with_openai(
    api_key: str,
    company_name: str,
    results: list[SearchResult],
) -> str | None:
    if not results:
        return None

    candidate_block = "\n".join(
        f"{index + 1}. title={result.title}\n   url={result.url}\n   content={(result.content or '')[:300]}"
        for index, result in enumerate(results[:10])
    )
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Pick the most likely official company website from the supplied search results. "
                    "Return only valid JSON with a single key named 'url'. If none look official, use null."
                ),
            },
            {
                "role": "user",
                "content": f"Company: {company_name}\n\nCandidates:\n{candidate_block}",
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    url = parsed.get("url")
    if isinstance(url, str) and url.strip():
        return url.strip()
    return None
