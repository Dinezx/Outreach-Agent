import asyncio
import httpx
from leadminerai.core.config import get_settings

async def test_tavily(tavily_key: str):
    print("--- Testing Tavily API Key ---")
    url = "https://api.tavily.com/search"
    payload = {"api_key": tavily_key, "query": "Python programming"}
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=payload, timeout=10.0)
            if r.status_code == 200:
                print("Tavily API key is VALID!")
                print("Result count:", len(r.json().get("results", [])))
            else:
                print(f"Tavily API key FAILED with status {r.status_code}: {r.text}")
        except Exception as e:
            print("Tavily API request error:", e)

async def test_openai(openai_key: str):
    print("\n--- Testing OpenAI API Key ---")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello, is this key valid? Answer in 3 words."}],
        "max_tokens": 10
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if r.status_code == 200:
                print("OpenAI API key is VALID!")
                print("Response:", r.json()["choices"][0]["message"]["content"].strip())
            else:
                print(f"OpenAI API key FAILED with status {r.status_code}: {r.text}")
        except Exception as e:
            print("OpenAI API request error:", e)

async def main():
    settings = get_settings()
    print("Settings DATABASE_URL:", settings.database_url)
    print("Tavily Key prefix:", settings.tavily_api_key[:12] if settings.tavily_api_key else "None")
    print("OpenAI Key prefix:", settings.openai_api_key[:12] if settings.openai_api_key else "None")
    
    await test_tavily(settings.tavily_api_key)
    await test_openai(settings.openai_api_key)

if __name__ == "__main__":
    asyncio.run(main())
