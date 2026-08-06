from __future__ import annotations

import json
import re
import httpx
from loguru import logger
from leadminerai.services.html_service import HTMLService


class ExtractorService:
    def __init__(self, openai_api_key: str | None = None) -> None:
        self.openai_api_key = openai_api_key

    async def extract(self, crawled_pages: dict[str, str], company_name: str) -> dict:
        if not crawled_pages:
            return self._empty_result()

        # Get base domain of the company website
        base_domain = ""
        for url in crawled_pages.keys():
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                netloc = parsed_url.netloc.lower()
                if netloc.startswith("www."):
                    netloc = netloc[4:]
                if netloc:
                    base_domain = netloc
                    break
            except Exception:
                pass

        aggregated = []
        for url, html in crawled_pages.items():
            cleaned = HTMLService.clean_html(html)
            aggregated.append(f"=== Page: {url} ===\n{cleaned}\n")
        
        pages_content = "\n".join(aggregated)
        
        if not self.openai_api_key or self.openai_api_key == "replace-me":
            logger.warning("OpenAI API Key is missing. Using heuristic extraction.")
            return self._heuristic_extract(pages_content, base_domain)

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI data extractor. Analyze the provided company website text content "
                        "and extract public contact information and decision makers. "
                        "Return a JSON object conforming exactly to this structure:\n"
                        "{\n"
                        "  \"contacts\": [\n"
                        "    {\n"
                        "      \"contact_type\": \"email\" | \"phone\" | \"address\" | \"social\" | \"map\",\n"
                        "      \"contact_value\": \"\",\n"
                        "      \"contact_label\": \"\",\n"
                        "      \"source_url\": \"\",\n"
                        "      \"confidence\": 96\n"
                        "    }\n"
                        "  ],\n"
                        "  \"decision_makers\": [\n"
                        "    {\n"
                        "      \"name\": \"\",\n"
                        "      \"designation\": \"\",\n"
                        "      \"linkedin_url\": \"\",\n"
                        "      \"source_url\": \"\",\n"
                        "      \"confidence\": 92\n"
                        "    }\n"
                        "  ]\n"
                        "}\n"
                        "Rules:\n"
                        "1. Verify that the contact details and decision makers are genuine and belong to the target company. Do NOT extract dummy/placeholder/mock/template emails (such as `info@example.com`, `test@test.com`, `user@domain.com`, `name@company.com`) or template phone numbers (such as `123-456-7890`, `999-999-9999`, `000-000-0000`, `1234567`).\n"
                        "2. Remove duplicate emails and phones.\n"
                        "3. Ignore personal emails like Gmail/Yahoo/Outlook unless they are the only contact info present on the official website.\n"
                        f"4. Verify that the email domains match the company's website domain (which is {base_domain}) or are generic public email providers (like gmail.com, yahoo.com). STRICTLY ignore emails from unrelated third-party websites or directory platforms.\n"
                        "5. Ensure the extracted locations, addresses, phone numbers, and decision makers are located in India (specifically Tamil Nadu region). Ignore contact details and decision makers that belong to offices/branches/teams in other countries.\n"
                        "6. Ignore emails belonging to foreign branches or offices outside India (such as those containing 'usa', 'cn', 'gulf', 'thailand', 'indonesia', 'vietnam', etc. in the email address).\n"
                        "7. Extract decision makers (look for CEO, COO, Managing Director, Plant Head, Operations Head, Production Manager, Purchase Manager, Supply Chain Manager, Warehouse Manager, Dispatch Manager, Quality Manager, Factory Manager, Maintenance Manager, Export Manager). Capture their Name, Designation, public LinkedIn URL (if public and listed), and the source_url of the page where you found them.\n"
                        "8. Ensure the source_url contains the exact crawled page URL (from the '=== Page: <URL> ===' headers) where the contact or decision maker was found.\n"
                        "9. Ensure confidence is an integer between 0 and 100.\n"
                        "Return ONLY valid raw JSON."
                    )
                },
                {
                    "role": "user",
                    "content": f"Company Name: {company_name}\n\nCrawled Website Content:\n{pages_content}"
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            # Post-process validation & priority assignment
            processed_contacts = []
            seen_contacts = set()
            personal_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"}
            placeholder_domains = {"example.com", "domain.com", "test.com", "email.com", "yourdomain.com", "template.com", "website.com"}
            placeholder_digits = {
                "1234567", "12345678", "123456789", "1234567890", 
                "9999999", "0000000", "00000000", "0000000000", "9999999999"
            }

            contacts_list = parsed.get("contacts", [])
            if not isinstance(contacts_list, list):
                contacts_list = []

            for c in contacts_list:
                if not isinstance(c, dict):
                    continue
                ctype = str(c.get("contact_type", "")).strip().lower()
                val = str(c.get("contact_value", "")).strip()
                label = str(c.get("contact_label", "")).strip()
                source = c.get("source_url") or ""
                conf = c.get("confidence") or 80
                try:
                    conf = int(conf)
                except Exception:
                    conf = 80

                if not val:
                    continue

                key = (ctype, val.lower())
                if key in seen_contacts:
                    continue

                # Validate Emails
                if ctype == "email":
                    domain = val.split("@")[-1].lower()
                    if domain in placeholder_domains:
                        continue
                    if base_domain and domain != base_domain and not domain.endswith("." + base_domain) and domain not in personal_domains:
                        continue
                    if not self._is_indian_email(val):
                        continue

                # Validate Phones
                elif ctype == "phone":
                    digits = re.sub(r'\D', '', val)
                    if not (7 <= len(digits) <= 15) or digits in placeholder_digits or digits.startswith("123456"):
                        continue
                    if len(set(digits)) < 3:
                        continue

                seen_contacts.add(key)
                
                # Dynamic priority calculation
                priority = self._calculate_priority(ctype, label, val)
                processed_contacts.append({
                    "contact_type": ctype,
                    "contact_value": val,
                    "contact_label": label,
                    "source_url": source,
                    "priority": priority,
                    "confidence": conf
                })

            # Post-process decision makers
            processed_dms = []
            seen_dms = set()
            dms_list = parsed.get("decision_makers", [])
            if not isinstance(dms_list, list):
                dms_list = []

            for dm in dms_list:
                if not isinstance(dm, dict):
                    continue
                name = str(dm.get("name", "")).strip()
                desig = str(dm.get("designation", "")).strip()
                lnk = dm.get("linkedin_url") or None
                source = dm.get("source_url") or ""
                conf = dm.get("confidence") or 80
                try:
                    conf = int(conf)
                except Exception:
                    conf = 80

                if not name or not desig:
                    continue

                dm_key = (name.lower(), desig.lower())
                if dm_key in seen_dms:
                    continue

                seen_dms.add(dm_key)
                priority = self._calculate_decision_maker_priority(desig)
                processed_dms.append({
                    "name": name,
                    "designation": desig,
                    "linkedin_url": lnk,
                    "source_url": source,
                    "priority": priority,
                    "confidence": conf
                })

            return {
                "contacts": processed_contacts,
                "decision_makers": processed_dms
            }

        except Exception as exc:
            logger.error(f"OpenAI extraction failed: {exc}. Falling back to heuristics.")
            return self._heuristic_extract(pages_content, base_domain)

    def _calculate_priority(self, ctype: str, label: str, value: str) -> int:
        label_lower = label.lower()
        val_lower = value.lower()
        
        if ctype == "email":
            if "purchase" in label_lower or "purchase" in val_lower or "procurement" in label_lower or "procurement" in val_lower:
                return 88
            if "export" in label_lower or "export" in val_lower:
                return 86
            if "sales" in label_lower or "sales" in val_lower or "marketing" in label_lower or "marketing" in val_lower:
                return 80
            if "service" in label_lower or "service" in val_lower or "support" in label_lower or "support" in val_lower or "customercare" in val_lower:
                return 60
            if "hr" in label_lower or "hr" in val_lower or "careers" in label_lower or "careers" in val_lower:
                return 30
            if "info" in label_lower or "info" in val_lower or "contact" in label_lower or "contact" in val_lower:
                return 20
            return 20

        elif ctype == "phone":
            if "mobile" in label_lower or "mob" in label_lower or val_lower.startswith("+919") or val_lower.startswith("919") or (len(re.sub(r'\D', '', val_lower)) == 10 and re.sub(r'\D', '', val_lower).startswith("9")):
                return 60
            if "toll" in label_lower or "free" in label_lower or "1800" in val_lower:
                return 40
            return 50

        elif ctype == "address":
            if "head" in label_lower or "hq" in label_lower or "corporate" in label_lower:
                return 70
            return 50

        elif ctype == "social":
            if "linkedin" in label_lower or "linkedin" in val_lower:
                return 60
            return 30

        elif ctype == "map":
            return 25

        return 20

    def _calculate_decision_maker_priority(self, designation: str) -> int:
        desig_lower = designation.lower()
        
        # Priority mapping from prompt + standard ranks
        if "operations manager" in desig_lower or "operations head" in desig_lower or "coo" in desig_lower:
            return 100
        if "plant head" in desig_lower:
            return 95
        if "production manager" in desig_lower or "production head" in desig_lower:
            return 90
        if "purchase manager" in desig_lower or "purchase head" in desig_lower or "procurement manager" in desig_lower:
            return 88
        if "quality manager" in desig_lower or "quality head" in desig_lower:
            return 82
        if "hr" in desig_lower or "human resource" in desig_lower:
            return 30
        
        # Other standard roles
        if "managing director" in desig_lower or "ceo" in desig_lower or "md" in desig_lower or "president" in desig_lower:
            return 92
        if "factory manager" in desig_lower or "general manager" in desig_lower or "gm" in desig_lower:
            return 87
        if "export manager" in desig_lower:
            return 86
        if "supply chain" in desig_lower or "logistics manager" in desig_lower or "dispatch manager" in desig_lower:
            return 85
        if "warehouse manager" in desig_lower:
            return 80
        if "maintenance manager" in desig_lower:
            return 75
            
        return 50

    def _is_indian_email(self, email: str) -> bool:
        email_lower = email.lower()
        if "@" not in email_lower:
            return False
        local_part = email_lower.split("@")[0]
        
        foreign_keywords = {
            "usa", "uk", "eu", "cn", "china", "indonesia", "gulf", "thailand", 
            "vietnam", "singapore", "malaysia", "europe", "australia", "russia", 
            "brazil", "japan", "korea", "canada", "mexico", "germany", "france"
        }
        
        import re
        tokens = set(re.split(r'[-._]', local_part))
        if any(k in local_part for k in foreign_keywords):
            return False
            
        return True

    def _empty_result(self) -> dict:
        return {
            "contacts": [],
            "decision_makers": []
        }

    def _heuristic_extract(self, content: str, base_domain: str = "") -> dict:
        # Extracted list
        contacts = []
        seen = set()

        # Find emails
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b'
        emails = re.findall(email_pattern, content)
        personal_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com"}
        placeholder_domains = {"example.com", "domain.com", "test.com", "email.com", "yourdomain.com", "template.com", "website.com"}

        for email in emails:
            email_clean = email.strip()
            domain = email_clean.split("@")[-1].lower()
            if domain not in placeholder_domains:
                if not base_domain or domain == base_domain or domain.endswith("." + base_domain) or domain in personal_domains:
                    if self._is_indian_email(email_clean):
                        key = ("email", email_clean.lower())
                        if key not in seen:
                            seen.add(key)
                            label = email_clean.split("@")[0] + "@"
                            contacts.append({
                                "contact_type": "email",
                                "contact_value": email_clean,
                                "contact_label": label,
                                "source_url": "",
                                "priority": self._calculate_priority("email", label, email_clean),
                                "confidence": 70
                            })

        # Find phones
        phone_pattern = r'\+?\(?\d{1,4}\)?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,9}'
        phones = re.findall(phone_pattern, content)
        placeholder_digits = {
            "1234567", "12345678", "123456789", "1234567890", 
            "9999999", "0000000", "00000000", "0000000000", "9999999999"
        }
        for p in phones:
            p_clean = p.strip().strip("-.,() ")
            digits = re.sub(r'\D', '', p_clean)
            if (7 <= len(digits) <= 15) and (digits not in placeholder_digits) and (not digits.startswith("123456")):
                if len(set(digits)) >= 3:
                    key = ("phone", digits)
                    if key not in seen:
                        seen.add(key)
                        label = "Office" if len(digits) > 10 or digits.startswith("0") else "Mobile"
                        contacts.append({
                            "contact_type": "phone",
                            "contact_value": p_clean,
                            "contact_label": label,
                            "source_url": "",
                            "priority": self._calculate_priority("phone", label, p_clean),
                            "confidence": 70
                        })

        # Find social links (LinkedIn Company, Facebook, Instagram, YouTube)
        social_patterns = {
            "LinkedIn": r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+',
            "Facebook": r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.-]+',
            "Instagram": r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.-]+',
            "YouTube": r'https?://(?:www\.)?youtube\.com/(?:channel|user|c)/[a-zA-Z0-9_-]+',
            "X": r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_-]+'
        }
        for label, pattern in social_patterns.items():
            matches = re.findall(pattern, content)
            for m in matches:
                key = ("social", m.lower())
                if key not in seen:
                    seen.add(key)
                    contacts.append({
                        "contact_type": "social",
                        "contact_value": m,
                        "contact_label": label,
                        "source_url": "",
                        "priority": self._calculate_priority("social", label, m),
                        "confidence": 80
                    })

        # Find Google Maps links
        maps_pattern = r'https?://(?:www\.)?(?:google\.com/maps|maps\.app\.goo\.gl)/[a-zA-Z0-9_.-@/+]+'
        maps_matches = re.findall(maps_pattern, content)
        for m in maps_matches:
            key = ("map", m.lower())
            if key not in seen:
                seen.add(key)
                contacts.append({
                    "contact_type": "map",
                    "contact_value": m,
                    "contact_label": "Google Maps",
                    "source_url": "",
                    "priority": 25,
                    "confidence": 80
                })

        return {
            "contacts": contacts,
            "decision_makers": []
        }
