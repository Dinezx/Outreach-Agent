from __future__ import annotations

import base64
from email.message import EmailMessage
import httpx
from loguru import logger


class GmailAPIService:
    GMAIL_BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"

    @staticmethod
    def create_mime_message(
        to_email: str,
        from_email: str,
        subject: str,
        body_text: str,
        thread_id: str | None = None,
        in_reply_to: str | None = None
    ) -> str:
        msg = EmailMessage()
        msg["To"] = to_email
        msg["From"] = from_email
        msg["Subject"] = subject
        msg.set_content(body_text)

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to

        raw_bytes = msg.as_bytes()
        encoded = base64.urlsafe_b64encode(raw_bytes).decode("utf-8")
        return encoded

    async def ensure_label_exists(self, access_token: str, label_name: str = "LeadMinerAI") -> str:
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # List existing labels
                resp = await client.get(f"{self.GMAIL_BASE_URL}/labels", headers=headers)
                if resp.status_code == 200:
                    labels = resp.json().get("labels", [])
                    for label in labels:
                        if label.get("name") == label_name:
                            return label.get("id")

                # Create label if not found
                payload = {
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show"
                }
                c_resp = await client.post(f"{self.GMAIL_BASE_URL}/labels", headers=headers, json=payload)
                if c_resp.status_code in (200, 201):
                    return c_resp.json().get("id", "LeadMinerAI")

        except Exception as exc:
            logger.warning(f"Could not inspect or create Gmail label '{label_name}': {exc}")

        return "LeadMinerAI"

    async def send_email(
        self,
        access_token: str,
        to_email: str,
        from_email: str,
        subject: str,
        body_text: str,
        thread_id: str | None = None,
        in_reply_to: str | None = None
    ) -> dict:
        label_id = await self.ensure_label_exists(access_token, "LeadMinerAI")

        raw_message = self.create_mime_message(
            to_email=to_email,
            from_email=from_email,
            subject=subject,
            body_text=body_text,
            thread_id=thread_id,
            in_reply_to=in_reply_to
        )

        payload = {
            "raw": raw_message,
        }
        if thread_id:
            payload["threadId"] = thread_id
        if label_id and label_id != "LeadMinerAI":
            payload["labelIds"] = [label_id]

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(f"{self.GMAIL_BASE_URL}/messages/send", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()

                return {
                    "gmail_message_id": data.get("id"),
                    "thread_id": data.get("threadId"),
                    "history_id": data.get("historyId"),
                    "label_id": label_id
                }
        except Exception as exc:
            logger.error(f"Gmail API messages.send failed: {exc}")
            raise RuntimeError(f"Gmail API message send failed: {exc}")

    async def poll_thread_replies(self, access_token: str, thread_id: str, sender_email: str) -> dict | None:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(f"{self.GMAIL_BASE_URL}/threads/{thread_id}", headers=headers)
                if resp.status_code != 200:
                    return None

                data = resp.json()
                messages = data.get("messages", [])
                for msg in messages:
                    payload = msg.get("payload", {})
                    msg_headers = {h.get("name", "").lower(): h.get("value", "") for h in payload.get("headers", [])}
                    msg_from = msg_headers.get("from", "")

                    # Check if message is incoming from recipient (not from system sender_email)
                    if sender_email.lower() not in msg_from.lower():
                        snippet = msg.get("snippet", "")
                        return {
                            "reply_id": msg.get("id"),
                            "reply_from": msg_from,
                            "reply_body": snippet,
                            "internal_date": msg.get("internalDate")
                        }
        except Exception as exc:
            logger.warning(f"Failed to poll thread {thread_id} replies: {exc}")

        return None
