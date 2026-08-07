from __future__ import annotations

from datetime import datetime, timedelta, timezone
import urllib.parse
import httpx
from loguru import logger

from leadminerai.services.crypto_service import CryptoService


class GmailAuthService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    DEFAULT_SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        redirect_uri: str,
        crypto_service: CryptoService
    ) -> None:
        self.client_id = client_id or "demo-google-client-id"
        self.client_secret = client_secret or "demo-google-client-secret"
        self.redirect_uri = redirect_uri
        self.crypto_service = crypto_service

    def generate_auth_url(self, state: str | None = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(self.DEFAULT_SCOPES),
        }
        if state:
            params["state"] = state
        return f"{self.GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code(self, code: str) -> dict:
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(self.GOOGLE_TOKEN_URL, data=data)
                resp.raise_for_status()
                token_data = resp.json()

                access_token = token_data.get("access_token")
                refresh_token = token_data.get("refresh_token", "")
                expires_in = token_data.get("expires_in", 3600)

                # Fetch user email address
                user_email = "authenticated.user@gmail.com"
                if access_token:
                    try:
                        u_resp = await client.get(
                            self.GOOGLE_USERINFO_URL,
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        if u_resp.status_code == 200:
                            user_email = u_resp.json().get("email", user_email)
                    except Exception as u_exc:
                        logger.warning(f"Could not fetch Google userinfo: {u_exc}")

                encrypted_refresh = self.crypto_service.encrypt_token(refresh_token) if refresh_token else ""
                expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                return {
                    "email": user_email,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "encrypted_refresh_token": encrypted_refresh,
                    "expiry": expiry,
                }
        except Exception as exc:
            logger.error(f"Google OAuth exchange_code failed: {exc}")
            raise RuntimeError(f"OAuth code exchange failed: {exc}")

    async def refresh_access_token(self, encrypted_refresh_token: str) -> dict:
        plain_refresh_token = self.crypto_service.decrypt_token(encrypted_refresh_token)
        if not plain_refresh_token:
            raise ValueError("No valid refresh token found to renew OAuth access")

        data = {
            "refresh_token": plain_refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(self.GOOGLE_TOKEN_URL, data=data)
                resp.raise_for_status()
                token_data = resp.json()

                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                return {
                    "access_token": access_token,
                    "expiry": expiry,
                }
        except Exception as exc:
            logger.error(f"Failed to refresh Google OAuth access token: {exc}")
            raise RuntimeError(f"Token refresh failed: {exc}")
