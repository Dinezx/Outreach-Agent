from __future__ import annotations

from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class HTMLService:
    @staticmethod
    def clean_html(html_content: str) -> str:
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "lxml")
        
        # Remove non-content, script, style, SVG, and layout metadata elements
        for element in soup([
            "script", "style", "svg", "noscript", "iframe", 
            "header", "footer", "head", "symbol", "path", "g", "style"
        ]):
            element.decompose()
            
        # Replace all links with formatted markdown text
        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            href = a.get("href", "").strip()
            
            if href.startswith("mailto:"):
                email_addr = href.replace("mailto:", "").split("?")[0].strip()
                if email_addr:
                    a.replace_with(f" [Email: {email_addr}] ")
                    continue
            elif href.startswith("tel:"):
                phone_num = href.replace("tel:", "").split("?")[0].strip()
                if phone_num:
                    a.replace_with(f" [Phone: {phone_num}] ")
                    continue

            if text and href:
                a.replace_with(f" [Link: {text}]({href}) ")
            elif text:
                a.replace_with(f" {text} ")
            else:
                a.decompose()
                
        # Get clean text separated by newlines
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines[:1000])  # limit length to avoid too many tokens

    @staticmethod
    def extract_links(html_content: str, base_url: str) -> list[str]:
        if not html_content:
            return []
        soup = BeautifulSoup(html_content, "lxml")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href:
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.append(normalized)
        return list(dict.fromkeys(links))
