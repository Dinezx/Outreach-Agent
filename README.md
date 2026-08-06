# LeadMinerAI

LeadMinerAI is an async FastAPI service that ingests CSV uploads of company names, stores them in PostgreSQL, and searches for official websites through the Tavily Search API.

## Features

- CSV upload for company names
- XLSX upload support for the same company_name/name column format
- Async SQLAlchemy repository/service layering
- Background search job to resolve official websites
- Optional OpenAI-backed ranking for search result selection
- PostgreSQL persistence with Alembic migrations
- Excel export of results
- Structured logging with Loguru
- Docker and Docker Compose support

## Local setup

1. Create a Python 3.11+ environment.
2. Install dependencies with `pip install -e .[dev]`.
3. Copy `.env.example` to `.env` and set `DATABASE_URL`, `TAVILY_API_KEY`, and `OPENAI_API_KEY` if you plan to use OpenAI-powered features.
4. Run migrations with `alembic upgrade head`.
5. Start the API with `uvicorn leadminerai.main:app --reload`.

If you exposed any real API keys while testing, rotate them before using the project in production.

## API

- `POST /api/v1/companies/upload`
- `POST /api/v1/companies/search/trigger`
- `GET /api/v1/companies`
- `GET /api/v1/companies/export`
