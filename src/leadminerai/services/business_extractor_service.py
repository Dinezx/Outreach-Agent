from __future__ import annotations

import json
import re
import httpx
from loguru import logger
from leadminerai.services.html_service import HTMLService


class BusinessExtractorService:
    def __init__(self, openai_api_key: str | None = None) -> None:
        self.openai_api_key = openai_api_key

    async def extract_business_intelligence(
        self,
        crawled_pages: dict[str, str],
        company_name: str
    ) -> dict:
        if not crawled_pages:
            return self._heuristic_fallback("", company_name)

        aggregated = []
        for url, html in crawled_pages.items():
            cleaned = HTMLService.clean_html(html)
            aggregated.append(f"=== Page: {url} ===\n{cleaned}\n")

        pages_content = "\n".join(aggregated)

        if not self.openai_api_key or self.openai_api_key == "replace-me":
            logger.warning("OpenAI API Key missing/invalid. Using heuristic business intelligence extraction.")
            return self._heuristic_fallback(pages_content, company_name)

        system_prompt = (
            "You are an expert Industrial & Business Operations Consultant. "
            "Analyze the provided text scraped from a company's public website and build a complete Business Profile.\n\n"
            "Return a single JSON object conforming EXACTLY to this schema:\n"
            "{\n"
            "  \"industry\": \"Manufacturing / Pumps / Automotive / etc.\",\n"
            "  \"sub_industry\": \"Specific sub-sector\",\n"
            "  \"description\": \"Comprehensive 2-3 sentence overview of business operations, products, and core capabilities.\",\n"
            "  \"products\": [\"Product 1\", \"Product 2\"],\n"
            "  \"services\": [\"Service 1\", \"Service 2\"],\n"
            "  \"manufacturing_type\": \"OEM / Contract Manufacturing / Job Work / Manufacturer / Exporter / Distributor / Supplier\",\n"
            "  \"departments\": [\n"
            "     {\"name\": \"Production\", \"confidence\": 95},\n"
            "     {\"name\": \"Quality\", \"confidence\": 90}\n"
            "  ],\n"
            "  \"locations\": [\"City / Plant Location 1\", \"Headquarters\"],\n"
            "  \"certifications\": [\"ISO 9001:2015\", \"IATF 16949\", \"CE\"],\n"
            "  \"markets\": [\"Domestic India\", \"Middle East\", \"Europe\"],\n"
            "  \"keywords\": [\"cnc machining\", \"submersible pumps\", \"casting\"],\n"
            "  \"predicted_pain_points\": [\n"
            "     {\n"
            "        \"name\": \"Production Planning & Scheduling Delays\",\n"
            "        \"severity\": 90,\n"
            "        \"frequency\": \"Daily\",\n"
            "        \"confidence\": 92\n"
            "     },\n"
            "     {\n"
            "        \"name\": \"Machine Downtime & Maintenance\",\n"
            "        \"severity\": 85,\n"
            "        \"frequency\": \"Weekly\",\n"
            "        \"confidence\": 88\n"
            "     }\n"
            "  ],\n"
            "  \"confidence\": 85\n"
            "}\n\n"
            "Rules:\n"
            "1. Think like an industrial consultant analyzing a client plant.\n"
            "2. Never hallucinate. If website content is very brief or missing, return an overall confidence score below 50.\n"
            "3. Predict operational departments (Production, Planning, Purchase, Stores, Warehouse, Dispatch, Logistics, Maintenance, Quality, Sales, HR, Finance) with individual confidence scores.\n"
            "4. Predict operational pain points specific to their industry (e.g. Inventory Visibility, Vendor Coordination, Machine Downtime, Quality Defect Tracking, Dispatch Delay, Energy Consumption).\n"
            "5. Assign severity (0-100), frequency ('Daily', 'Weekly', 'Monthly'), and confidence (0-100) to each predicted pain point.\n"
            "6. Extract all certifications (ISO, TS, CE, UL, RoHS, etc.) and factory/office locations.\n"
            "7. Return ONLY raw valid JSON."
        )

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Company Name: {company_name}\n\nCrawled Website Text:\n{pages_content[:15000]}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()

            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            # Ensure all required fields exist with correct fallback types
            return {
                "industry": str(parsed.get("industry") or "Industrial Manufacturing"),
                "sub_industry": str(parsed.get("sub_industry") or "General Engineering"),
                "description": str(parsed.get("description") or f"{company_name} is an industrial equipment and manufacturing provider."),
                "products": list(parsed.get("products") or []),
                "services": list(parsed.get("services") or []),
                "manufacturing_type": str(parsed.get("manufacturing_type") or "Manufacturer"),
                "departments": list(parsed.get("departments") or []),
                "locations": list(parsed.get("locations") or []),
                "certifications": list(parsed.get("certifications") or []),
                "markets": list(parsed.get("markets") or []),
                "keywords": list(parsed.get("keywords") or []),
                "pain_points": list(parsed.get("predicted_pain_points") or []),
                "confidence": int(parsed.get("confidence") or 75)
            }

        except Exception as exc:
            logger.error(f"OpenAI business extraction failed: {exc}. Using heuristic fallback.")
            return self._heuristic_fallback(pages_content, company_name)

    def _heuristic_fallback(self, content: str, company_name: str) -> dict:
        content_lower = content.lower()

        # Certifications detection
        certifications = []
        iso_matches = re.findall(r'iso\s*\d{4,5}(?::\d{4})?', content, re.IGNORECASE)
        for m in iso_matches:
            c = m.strip().upper()
            if c not in certifications:
                certifications.append(c)
        if "ce" in content_lower and "CE" not in certifications:
            certifications.append("CE Mark")
        if "rohs" in content_lower and "RoHS" not in certifications:
            certifications.append("RoHS Compliant")

        # Industry detection heuristics
        industry = "Industrial Manufacturing"
        sub_industry = "Engineering Components"
        manufacturing_type = "Manufacturer"

        if "pump" in content_lower or "valve" in content_lower or "motor" in content_lower:
            industry = "Flow Control & Pumps"
            sub_industry = "Pumps & Valves Manufacturing"
            manufacturing_type = "OEM & Manufacturer"
        elif "cnc" in content_lower or "machining" in content_lower or "lathe" in content_lower or "precision" in content_lower:
            industry = "Precision Engineering"
            sub_industry = "CNC Machined Components"
            manufacturing_type = "Contract Manufacturing & Job Work"
        elif "textile" in content_lower or "weaving" in content_lower or "yarn" in content_lower:
            industry = "Textiles & Machinery"
            sub_industry = "Textile Equipment"
        elif "auto" in content_lower or "automotive" in content_lower or "vehicle" in content_lower:
            industry = "Automotive Components"
            sub_industry = "Auto Ancillary"
            manufacturing_type = "OEM Supplier"
        elif "chemical" in content_lower or "pharma" in content_lower or "process" in content_lower:
            industry = "Chemical & Process Industry"
            sub_industry = "Process Equipment"

        # Products heuristics
        products = []
        product_matches = re.findall(r'(?:product|offering|range)s?:\s*([^\n.]+)', content, re.IGNORECASE)
        for pm in product_matches:
            items = [x.strip() for x in pm.split(",") if len(x.strip()) > 3]
            products.extend(items[:5])
        if not products:
            products = [f"{industry} Products", "Engineered Assemblies"]

        # Department predictions
        departments = [
            {"name": "Production", "confidence": 95},
            {"name": "Quality Assurance", "confidence": 90},
            {"name": "Purchase & Procurement", "confidence": 88},
            {"name": "Stores & Warehouse", "confidence": 85},
            {"name": "Maintenance", "confidence": 82},
            {"name": "Dispatch & Logistics", "confidence": 80},
            {"name": "Sales & Marketing", "confidence": 85},
            {"name": "HR & Admin", "confidence": 75}
        ]

        # Operational Pain Points prediction
        pain_points = [
            {
                "name": "Production Planning & Scheduling Delays",
                "severity": 90,
                "frequency": "Daily",
                "confidence": 88
            },
            {
                "name": "Machine Downtime & Maintenance Tracking",
                "severity": 85,
                "frequency": "Weekly",
                "confidence": 85
            },
            {
                "name": "Raw Material & Inventory Visibility",
                "severity": 88,
                "frequency": "Daily",
                "confidence": 86
            },
            {
                "name": "Vendor & Subcontractor Lead Time Coordination",
                "severity": 80,
                "frequency": "Weekly",
                "confidence": 82
            },
            {
                "name": "Quality Defect & Rejection Tracking",
                "severity": 82,
                "frequency": "Daily",
                "confidence": 84
            }
        ]

        # Locations detection
        locations = []
        city_matches = re.findall(r'(?:chennai|coimbatore|bangalore|mumbai|pune|hyderabad|delhi|ahmedabad|gurgaon|noida|kolkata)', content, re.IGNORECASE)
        for cm in city_matches:
            loc = cm.capitalize()
            if loc not in locations:
                locations.append(loc)
        if not locations:
            locations = ["Tamil Nadu, India"]

        desc = f"{company_name} is an established company in the {industry} sector specializing in {sub_industry} and industrial solutions."

        confidence = 70 if content else 45

        return {
            "industry": industry,
            "sub_industry": sub_industry,
            "description": desc,
            "products": products[:10],
            "services": ["Custom Manufacturing", "Technical Support", "Product Servicing"],
            "manufacturing_type": manufacturing_type,
            "departments": departments,
            "locations": locations,
            "certifications": certifications or ["ISO 9001 Certified"],
            "markets": ["Domestic India", "Export Markets"],
            "keywords": [industry.lower(), sub_industry.lower(), "manufacturing", "engineering"],
            "pain_points": pain_points,
            "confidence": confidence
        }
