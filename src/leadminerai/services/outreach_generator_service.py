from __future__ import annotations

import json
import re
import time
import httpx
from loguru import logger


class OutreachGeneratorService:
    def __init__(self, openai_api_key: str | None = None) -> None:
        self.openai_api_key = openai_api_key

    def evaluate_contacts_and_channels(
        self,
        contacts: list[dict],
        decision_makers: list[dict],
        company_website: str | None = None
    ) -> tuple[dict | None, str, str, int, str]:
        """
        Selects best contact and ranks best channel based on priority rules.
        Returns: (best_contact_dict, target_role, best_channel, channel_confidence, reason)
        """
        role_priority = [
            "Operations Manager",
            "Plant Head",
            "Production Manager",
            "Purchase Manager",
            "Warehouse Manager",
            "Quality Manager",
            "Factory Manager",
        ]

        best_dm = None
        best_role = "General Operations Team"
        reason = "General corporate inquiry channel selected."

        # Search decision makers for target roles
        for role in role_priority:
            for dm in decision_makers:
                desig = dm.get("designation", "")
                if role.lower() in desig.lower():
                    best_dm = dm
                    best_role = desig
                    reason = f"Identified {best_role} who oversees core production, planning, and operational processes."
                    break
            if best_dm:
                break

        if not best_dm and decision_makers:
            best_dm = decision_makers[0]
            best_role = best_dm.get("designation", "Key Decision Maker")
            reason = f"Selected {best_dm.get('name')} ({best_role}) as primary operational leadership contact."

        # Evaluate best channel
        best_channel = "office_email"
        channel_confidence = 75

        # Check for emails in contacts or decision makers
        has_email = any(c.get("contact_type") == "email" for c in contacts)
        has_phone = any(c.get("contact_type") == "phone" for c in contacts)
        has_linkedin = (best_dm and best_dm.get("linkedin_url")) or any(c.get("contact_type") == "social" for c in contacts)

        if has_email:
            best_channel = "office_email"
            channel_confidence = 95
        elif has_linkedin:
            best_channel = "linkedin_dm"
            channel_confidence = 88
        elif has_phone:
            best_channel = "phone_script"
            channel_confidence = 82
        elif company_website:
            best_channel = "website_contact_form"
            channel_confidence = 70
        else:
            best_channel = "office_email"
            channel_confidence = 60

        return best_dm, best_role, best_channel, channel_confidence, reason

    async def generate_outreach(
        self,
        company_name: str,
        company_intel: dict,
        contacts: list[dict],
        decision_makers: list[dict],
        website_url: str | None = None
    ) -> dict:
        start_time = time.time()

        best_dm, target_role, best_channel, channel_conf, reason = self.evaluate_contacts_and_channels(
            contacts, decision_makers, website_url
        )

        dm_name = best_dm.get("name") if best_dm else None
        industry = company_intel.get("industry") or "Industrial Manufacturing"
        products = company_intel.get("products") or []
        mfg_type = company_intel.get("manufacturing_type") or "Manufacturer"
        locations = company_intel.get("locations") or ["Tamil Nadu"]
        pain_points = company_intel.get("pain_points") or []

        location_str = locations[0] if locations else "Tamil Nadu"
        products_str = ", ".join(products[:3]) if products else "industrial products"

        prompt_tokens = 0
        completion_tokens = 0

        if not self.openai_api_key or self.openai_api_key == "replace-me":
            logger.warning("OpenAI API key missing. Using heuristic research outreach generator.")
            result = self._heuristic_generate(
                company_name, dm_name, target_role, industry, products_str, location_str, best_channel, channel_conf, reason
            )
            result["generation_time_ms"] = int((time.time() - start_time) * 1000)
            result["prompt_tokens"] = 0
            result["completion_tokens"] = 0
            result["contact"] = best_dm
            return result

        system_prompt = (
            "You are Dinesh Kumar, an independent industrial research scholar conducting an empirical study on "
            "operational challenges, supply chain lead times, and maintenance bottlenecks in manufacturing enterprises across Tamil Nadu.\n\n"
            "CRITICAL RULES:\n"
            "1. THIS IS FOR INDEPENDENT ACADEMIC / INDUSTRIAL RESEARCH ONLY.\n"
            "2. NEVER SELL ANYTHING. NO SOFTWARE PITCHES, NO SERVICES, NO MARKETING AGENDAS.\n"
            "3. EMAIL BODY MUST BE STRICTLY UNDER 180 WORDS.\n"
            "4. LINKEDIN MESSAGE MUST BE STRICTLY UNDER 300 CHARACTERS.\n"
            "5. REFERENCE THE COMPANY'S ACTUAL INDUSTRY AND PRODUCTS TO SHOW SINCERE PREPARATION.\n"
            "6. DO NOT FABRICATE OR HALLUCINATE FACTS.\n\n"
            "Return a JSON object conforming exactly to:\n"
            "{\n"
            "  \"subject\": \"Research Brief: Operational & Production Study - [Company Name]\",\n"
            "  \"email_body\": \"Dear [Name/Team], ... [120-180 words] ... Warm regards,\\nDinesh Kumar\\nIndependent Operations Researcher\",\n"
            "  \"linkedin_message\": \"Hello [Name], I am conducting a research study on manufacturing operations in Tamil Nadu... [Max 300 chars]\",\n"
            "  \"phone_script\": \"Hello, My name is Dinesh Kumar. I am conducting an independent research study...\",\n"
            "  \"overall_confidence\": 90\n"
            "}"
        )

        user_content = (
            f"Company Name: {company_name}\n"
            f"Target Contact Person: {dm_name or 'Operations Lead'}\n"
            f"Target Role/Designation: {target_role}\n"
            f"Industry: {industry}\n"
            f"Manufacturing Type: {mfg_type}\n"
            f"Key Products: {products_str}\n"
            f"Location: {location_str}\n"
            f"Identified Pain Points: {[p.get('name') if isinstance(p, dict) else p for p in pain_points[:2]]}\n"
        )

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=40.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
                    json=payload
                )
                resp.raise_for_status()
                data = resp.json()

            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)

            email_body = parsed.get("email_body", "")
            # Ensure email body word count limit
            words = email_body.split()
            if len(words) > 180:
                email_body = " ".join(words[:180]) + "\n\nWarm regards,\nDinesh Kumar\nIndependent Industrial Researcher"

            linkedin_msg = parsed.get("linkedin_message", "")
            if len(linkedin_msg) > 300:
                linkedin_msg = linkedin_msg[:297] + "..."

            overall_conf = int(parsed.get("overall_confidence") or 85)

            # If confidence is below 70, use generic research template fallback
            if overall_conf < 70:
                return self._generic_research_fallback(
                    company_name, dm_name, target_role, best_channel, channel_conf, reason,
                    int((time.time() - start_time) * 1000), prompt_tokens, completion_tokens, best_dm
                )

            return {
                "subject": parsed.get("subject", f"Research Study Invitation: Manufacturing Operations - {company_name}"),
                "email_body": email_body,
                "linkedin_message": linkedin_msg,
                "phone_script": parsed.get("phone_script", f"Hello, My name is Dinesh Kumar. I am conducting an independent research study on manufacturing operations in {location_str}..."),
                "channel": best_channel,
                "target_role": target_role,
                "recommendation_reason": reason,
                "channel_confidence": channel_conf,
                "overall_confidence": overall_conf,
                "generation_time_ms": int((time.time() - start_time) * 1000),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "contact": best_dm
            }

        except Exception as exc:
            logger.error(f"OpenAI outreach generation failed: {exc}. Using heuristic fallback.")
            result = self._heuristic_generate(
                company_name, dm_name, target_role, industry, products_str, location_str, best_channel, channel_conf, reason
            )
            result["generation_time_ms"] = int((time.time() - start_time) * 1000)
            result["prompt_tokens"] = 0
            result["completion_tokens"] = 0
            result["contact"] = best_dm
            return result

    def _heuristic_generate(
        self,
        company_name: str,
        dm_name: str | None,
        target_role: str,
        industry: str,
        products_str: str,
        location_str: str,
        best_channel: str,
        channel_conf: int,
        reason: str
    ) -> dict:
        greeting = f"Dear {dm_name}," if dm_name else f"Dear {target_role} / Operations Team,"

        subject = f"Industrial Research Brief: Operational Efficiency Study - {company_name}"

        email_body = (
            f"{greeting}\n\n"
            f"My name is Dinesh Kumar, an independent researcher studying industrial operations and supply chain efficiency across manufacturing firms in {location_str}.\n\n"
            f"We are currently examining operational workflows specifically in the {industry} sector, with a focus on companies producing {products_str}. "
            f"Our study aims to benchmark production planning, preventive maintenance schedules, and material handling lead times.\n\n"
            f"This is strictly a non-commercial academic research initiative. We are not offering or selling any software or commercial services.\n\n"
            f"Would you be open to a brief 10-minute telephone discussion or completing a short 5-question research survey at your convenience?\n\n"
            f"Warm regards,\n"
            f"Dinesh Kumar\n"
            f"Independent Operations Scholar & Researcher"
        )

        # Ensure under 180 words
        words = email_body.split()
        if len(words) > 180:
            email_body = " ".join(words[:180])

        linkedin_msg = (
            f"Hi {dm_name or 'there'}, I'm Dinesh Kumar, conducting an independent research study on manufacturing operations in {location_str}. "
            f"I'm not selling any software. Would love to connect and share our brief 5-question industry benchmark survey!"
        )[:300]

        phone_script = (
            f"Hello,\n"
            f"My name is Dinesh Kumar.\n"
            f"I am conducting an independent research study on operational challenges and production planning faced by manufacturing companies in {location_str}.\n"
            f"I am not selling any software or services.\n"
            f"Would it be possible to speak with your {target_role} for 10 minutes, or share the best email to send our brief 5-question research survey?"
        )

        return {
            "subject": subject,
            "email_body": email_body,
            "linkedin_message": linkedin_msg,
            "phone_script": phone_script,
            "channel": best_channel,
            "target_role": target_role,
            "recommendation_reason": reason,
            "channel_confidence": channel_conf,
            "overall_confidence": 82
        }

    def _generic_research_fallback(
        self,
        company_name: str,
        dm_name: str | None,
        target_role: str,
        best_channel: str,
        channel_conf: int,
        reason: str,
        gen_time: int,
        p_tokens: int,
        c_tokens: int,
        best_dm: dict | None
    ) -> dict:
        greeting = f"Dear {dm_name}," if dm_name else "Dear Operations & Factory Management Team,"

        subject = f"Academic Research Survey Invitation: Manufacturing Operations Study"

        email_body = (
            f"{greeting}\n\n"
            f"My name is Dinesh Kumar, conducting an independent research survey on operational practices in manufacturing companies.\n\n"
            f"We are collecting insights on plant scheduling, maintenance, and supply chain coordination for academic benchmarking. "
            f"This study is strictly non-commercial and we are not selling any software or services.\n\n"
            f"We would greatly appreciate 5 minutes of your time to participate in our research study.\n\n"
            f"Warm regards,\n"
            f"Dinesh Kumar\n"
            f"Independent Researcher"
        )

        linkedin_msg = (
            f"Hello, I am conducting an independent research study on manufacturing operations in Tamil Nadu. "
            f"No software sales involved. Would appreciate 5 minutes of your time for our research survey!"
        )[:300]

        phone_script = (
            "Hello, My name is Dinesh Kumar. I am conducting an independent research study on operational challenges "
            "faced by manufacturing companies in Tamil Nadu. I am not selling any software. Would it be possible to speak "
            "with your Operations Manager for 10 minutes?"
        )

        return {
            "subject": subject,
            "email_body": email_body,
            "linkedin_message": linkedin_msg,
            "phone_script": phone_script,
            "channel": best_channel,
            "target_role": target_role,
            "recommendation_reason": "Low confidence or sparse website data: generated generic research invitation.",
            "channel_confidence": channel_conf,
            "overall_confidence": 65,
            "generation_time_ms": gen_time,
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "contact": best_dm
        }
