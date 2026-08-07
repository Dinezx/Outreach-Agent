from __future__ import annotations

import json
import re
import httpx
from loguru import logger
from leadminerai.services.html_service import HTMLService


class ExtractorService:
    def __init__(self, openai_api_key: str | None = None) -> None:
        self.openai_api_key = openai_api_key

    @staticmethod
    def clean_and_format_phone(phone_str: str) -> tuple[str | None, str]:
        """
        Validates a raw phone string and formats it cleanly into standard Indian/International formats.
        Returns (formatted_phone_string, label) or (None, "") if invalid.
        """
        if not phone_str:
            return None, ""
            
        phone_str = phone_str.strip()
        
        # 1. Reject if it contains decimal points (coordinates, float CSS numbers, e.g. "46 61.76 10.32", "22.90 18.07 44")
        if "." in phone_str:
            return None, ""

        # 2. Reject ISO standards, certifications, years, postal codes, range numbers
        phone_lower = phone_str.lower()
        if any(term in phone_lower for term in ["iso", "9001", "14001", "45001", "certif", "standard", "pincode"]):
            return None, ""
            
        # Reject year range like 2020-2030, 2023-2030, 2015-2020
        if re.search(r'20[0-9]{2}[-\s]?20[0-9]{2}', phone_str):
            return None, ""

        # 3. Reject 4 or 5 space-separated 2-digit pairs without country code (e.g. "32 36 58 14 44", "36 35 32 40 29")
        tokens = phone_str.split()
        if len(tokens) >= 4 and all(len(t) == 2 and t.isdigit() for t in tokens):
            if not phone_str.startswith("+"):
                return None, ""

        # 4. Extract digits
        digits = re.sub(r'\D', '', phone_str)
        
        if len(digits) < 7 or len(digits) > 15:
            return None, ""
        if len(set(digits)) < 3:
            return None, ""
        if digits in {"1234567890", "123456789", "0123456789", "9876543210"} or digits.startswith("123456"):
            return None, ""

        # 5. Format validation
        # Indian Toll Free: 1800 XXX XXXX
        if digits.startswith("1800") and (len(digits) == 10 or len(digits) == 11):
            formatted = f"1800-{digits[4:7]}-{digits[7:]}"
            return formatted, "Toll-Free"

        # Indian Mobile: Starts with +91/91/0 or 10 digits starting with 6,7,8,9
        if digits.startswith("91") and len(digits) == 12 and digits[2] in "6789":
            mob_digits = digits[2:]
            formatted = f"+91 {mob_digits[:5]} {mob_digits[5:]}"
            return formatted, "Mobile"
            
        if digits.startswith("0") and len(digits) == 11 and digits[1] in "6789":
            mob_digits = digits[1:]
            formatted = f"+91 {mob_digits[:5]} {mob_digits[5:]}"
            return formatted, "Mobile"

        if len(digits) == 10 and digits[0] in "6789":
            formatted = f"+91 {digits[:5]} {digits[5:]}"
            return formatted, "Mobile"

        # Indian Landline / STD: 0 + Area Code + Local Number
        if digits.startswith("0") and len(digits) in (10, 11) and digits[1] in "12345":
            if digits.startswith("044") or digits.startswith("080") or digits.startswith("022") or digits.startswith("011") or digits.startswith("033") or digits.startswith("040"):
                formatted = f"{digits[:3]}-{digits[3:]}"
            elif digits.startswith("0422") or digits.startswith("0522") or digits.startswith("0421") or digits.startswith("0452") or digits.startswith("0431"):
                formatted = f"{digits[:4]}-{digits[4:]}"
            else:
                formatted = f"{digits[:4]}-{digits[4:]}"
            return formatted, "Office"

        if digits.startswith("91") and len(digits) in (11, 12) and digits[2] in "12345":
            std_and_local = digits[2:]
            formatted = f"0{std_and_local[:3]}-{std_and_local[3:]}"
            return formatted, "Office"

        # Valid International format starting with +
        if phone_str.startswith("+") and len(digits) >= 8:
            formatted = f"+{digits}"
            return formatted, "International"

        # Landlines missing leading zero (e.g. 4425340523 -> 044-25340523)
        if len(digits) == 10 and (digits.startswith("44") or digits.startswith("80") or digits.startswith("22") or digits.startswith("11")):
            formatted = f"0{digits[:2]}-{digits[2:]}"
            return formatted, "Office"

        if len(digits) == 11 and (digits.startswith("422") or digits.startswith("522")):
            formatted = f"0{digits[:3]}-{digits[3:]}"
            return formatted, "Office"

        return None, ""

    @staticmethod
    def clean_and_format_email(email_str: str, base_domain: str = "") -> str | None:
        if not email_str:
            return None
        email_str = email_str.strip().lower()
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}$'
        if not re.match(email_pattern, email_str):
            return None
            
        domain = email_str.split("@")[-1]
        local_part = email_str.split("@")[0]
        
        placeholder_domains = {
            "example.com", "domain.com", "test.com", "email.com", "yourdomain.com", 
            "template.com", "website.com", "sentry.io", "wix.com", "wordpress.com", "schema.org"
        }
        if domain in placeholder_domains:
            return None
            
        placeholder_locals = {"user", "name", "email", "yourname", "test", "demo"}
        if local_part in placeholder_locals:
            return None

        personal_domains = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "yahoo.co.in", "rediffmail.com"}
        if base_domain:
            if domain != base_domain and not domain.endswith("." + base_domain) and domain not in personal_domains:
                return None
                
        # Foreign email filter
        foreign_keywords = {
            "usa", "uk", "eu", "cn", "china", "indonesia", "gulf", "thailand", 
            "vietnam", "singapore", "malaysia", "europe", "australia", "russia", 
            "brazil", "japan", "korea", "canada", "mexico", "germany", "france"
        }
        tokens = set(re.split(r'[-._]', local_part))
        if any(k in tokens for k in foreign_keywords):
            return None

        return email_str

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
                        "1. Verify that contact details belong to the target company. Do NOT extract dummy/placeholder emails or template numbers.\n"
                        "2. STRICT RULE FOR PHONE NUMBERS: Extract ONLY genuine official Indian or International business contact phone numbers (e.g. +91 98765 43210, 044-25340523, 1800-XXX-XXXX). STRICTLY IGNORE: layout numbers, 5 space-separated 2-digit numbers (such as 32 36 58 14 44), coordinate numbers containing decimals (such as 46 61.76 10.32), ISO standard codes (such as ISO 9001:2015), year ranges (such as 2023-2030), pincodes, or font sizes.\n"
                        "3. Remove duplicate emails and phones.\n"
                        f"4. Verify that email domains match the company website domain ({base_domain}) or generic providers (gmail.com, yahoo.com). Ignore emails from unrelated third-party sites.\n"
                        "5. Ensure extracted contact details and decision makers belong to India (specifically Tamil Nadu region if applicable).\n"
                        "6. Extract decision makers (CEO, COO, Managing Director, Plant Head, Operations Head, Production Manager, Purchase Manager, Quality Manager, Factory Manager, Export Manager). Capture Name, Designation, public LinkedIn URL, and source_url.\n"
                        "7. Return ONLY valid raw JSON."
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

                # Validate & format Email
                if ctype == "email":
                    clean_email = self.clean_and_format_email(val, base_domain)
                    if not clean_email:
                        continue
                    val = clean_email
                    label = label or (clean_email.split("@")[0] + "@")

                # Validate & format Phone
                elif ctype == "phone":
                    formatted_phone, detected_label = self.clean_and_format_phone(val)
                    if not formatted_phone:
                        continue
                    val = formatted_phone
                    label = label or detected_label

                key = (ctype, val.lower())
                if key in seen_contacts:
                    continue

                seen_contacts.add(key)
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
            if "mobile" in label_lower or "mob" in label_lower or val_lower.startswith("+91 9") or val_lower.startswith("+91 8") or val_lower.startswith("+91 7") or val_lower.startswith("+91 6"):
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

    def _empty_result(self) -> dict:
        return {
            "contacts": [],
            "decision_makers": []
        }

    def _heuristic_extract(self, content: str, base_domain: str = "") -> dict:
        contacts = []
        seen = set()

        # 1. Find emails (from text and [Email: ...] tags)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}'
        emails = re.findall(email_pattern, content)

        for email in emails:
            clean_email = self.clean_and_format_email(email, base_domain)
            if clean_email:
                key = ("email", clean_email)
                if key not in seen:
                    seen.add(key)
                    label = clean_email.split("@")[0] + "@"
                    contacts.append({
                        "contact_type": "email",
                        "contact_value": clean_email,
                        "contact_label": label,
                        "source_url": "",
                        "priority": self._calculate_priority("email", label, clean_email),
                        "confidence": 75
                    })

        # 2. Find phones using precise regexes
        phone_candidates = []

        # Extract from [Phone: ...] links
        phone_links = re.findall(r'\[Phone:\s*([^\]]+)\]', content)
        phone_candidates.extend(phone_links)

        # Indian Mobile numbers (+91 9XXXX XXXXX, 09XXXX XXXXX, 9XXXXXXXXX)
        mobiles = re.findall(r'(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b', content)
        phone_candidates.extend(mobiles)

        # Indian Landline / STD numbers (044-25340523, 0422-2223512, 080-41141264, +91-44-25340523)
        landlines = re.findall(r'(?:\+91[\s-]?)?0\d{2,4}[\s-]?\d{6,8}\b', content)
        phone_candidates.extend(landlines)

        # Toll-free numbers
        toll_frees = re.findall(r'\b1800[\s-]?\d{3}[\s-]?\d{4}\b', content)
        phone_candidates.extend(toll_frees)

        # International format starting with +
        internationals = re.findall(r'\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}\b', content)
        phone_candidates.extend(internationals)

        for raw_p in phone_candidates:
            formatted_p, label = self.clean_and_format_phone(raw_p)
            if formatted_p:
                key = ("phone", formatted_p.lower())
                if key not in seen:
                    seen.add(key)
                    contacts.append({
                        "contact_type": "phone",
                        "contact_value": formatted_p,
                        "contact_label": label,
                        "source_url": "",
                        "priority": self._calculate_priority("phone", label, formatted_p),
                        "confidence": 75
                    })

        # 3. Find social links
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

        # 4. Find Google Maps links
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
