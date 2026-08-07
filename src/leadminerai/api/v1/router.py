from fastapi import APIRouter

from leadminerai.api.v1.companies import router as companies_router
from leadminerai.api.v1.intelligence import router as intelligence_router
from leadminerai.api.v1.business_intelligence import router as business_intelligence_router
from leadminerai.api.v1.outreach import router as outreach_router

api_router = APIRouter()
api_router.include_router(companies_router, prefix="/companies", tags=["companies"])
api_router.include_router(intelligence_router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(business_intelligence_router, prefix="/business-intelligence", tags=["business-intelligence"])
api_router.include_router(outreach_router)


