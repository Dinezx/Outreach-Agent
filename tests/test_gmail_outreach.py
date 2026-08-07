from __future__ import annotations

import pytest
from httpx import AsyncClient

from leadminerai.services.crypto_service import CryptoService
from leadminerai.services.gmail_auth_service import GmailAuthService
from leadminerai.services.gmail_service import GmailAPIService
from leadminerai.repositories.gmail_repository import GmailRepository
from leadminerai.repositories.company_repository import CompanyRepository


def test_crypto_service():
    crypto = CryptoService()
    secret_token = "1//04_fake_google_refresh_token_xyz_123"

    encrypted = crypto.encrypt_token(secret_token)
    assert encrypted != secret_token
    assert len(encrypted) > 10

    decrypted = crypto.decrypt_token(encrypted)
    assert decrypted == secret_token


def test_gmail_auth_service_url():
    crypto = CryptoService()
    auth_service = GmailAuthService(
        client_id="test-client-id.apps.googleusercontent.com",
        client_secret="test-client-secret",
        redirect_uri="http://localhost:8000/api/gmail/oauth2callback",
        crypto_service=crypto
    )

    url = auth_service.generate_auth_url(state="test_state_123")
    assert "https://accounts.google.com/o/oauth2/v2/auth" in url
    assert "client_id=test-client-id" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fgmail%2Foauth2callback" in url
    assert "scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.send" in url
    assert "state=test_state_123" in url


def test_mime_message_creation():
    raw_encoded = GmailAPIService.create_mime_message(
        to_email="suresh.kumar@apexvalves.com",
        from_email="dineshkumarsaj@gmail.com",
        subject="Industrial Research Survey Invitation",
        body_text="Dear Suresh Kumar,\nWe invite you to participate in our operations benchmarking research."
    )
    assert len(raw_encoded) > 50
    assert not raw_encoded.startswith("Subject:")  # Encoded base64 string


@pytest.mark.asyncio
async def test_gmail_repository(test_app):
    sessionmaker = test_app.state.database.sessionmaker

    async with sessionmaker() as session:
        crypto = CryptoService()
        repo = GmailRepository(session)

        # 1. Upsert account
        account = await repo.upsert_account(
            email="dineshkumarsaj@gmail.com",
            encrypted_refresh_token=crypto.encrypt_token("ref_token_123"),
            access_token="acc_token_456"
        )
        assert account.email == "dineshkumarsaj@gmail.com"
        assert account.is_active is True

        # 2. Get active account
        active = await repo.get_active_account()
        assert active is not None
        assert active.id == account.id

        # 3. Create message
        msg_data = {
            "gmail_account_id": account.id,
            "subject": "Research Study: Manufacturing Technology",
            "body": "Hello, conducting research...",
            "recipient_email": "plant.head@texmopumps.com",
            "sender_email": account.email,
            "status": "DRAFT"
        }
        msg = await repo.create_message(msg_data)
        assert msg.id is not None
        assert msg.status == "DRAFT"

        # 4. Update status to SENT
        sent_msg = await repo.update_message_status(
            message_id=msg.id,
            status="SENT",
            gmail_msg_id="gmail_msg_id_999",
            thread_id="thread_id_888",
            history_id="hist_123"
        )
        assert sent_msg.status == "SENT"
        assert sent_msg.gmail_message_id == "gmail_msg_id_999"
        assert sent_msg.thread_id == "thread_id_888"

        # 5. Record reply
        replied_msg = await repo.record_reply(
            message_id=msg.id,
            reply_from="plant.head@texmopumps.com",
            reply_body="Thank you. We are interested in participating."
        )
        assert replied_msg.status == "REPLIED"
        assert replied_msg.is_reply is True
        assert "interested" in replied_msg.reply_body

        # 6. Schedule follow-up
        followed_msg = await repo.schedule_follow_up(msg.id, days=3)
        assert followed_msg.status == "FOLLOW_UP"
        assert followed_msg.follow_up_count == 1
        assert followed_msg.scheduled_follow_up_at is not None


@pytest.mark.asyncio
async def test_gmail_api_endpoints(client: AsyncClient, test_app):
    sessionmaker = test_app.state.database.sessionmaker
    async with sessionmaker() as session:
        crypto = CryptoService()
        repo = GmailRepository(session)
        await repo.upsert_account(
            email="dineshkumarsaj@gmail.com",
            encrypted_refresh_token=crypto.encrypt_token("ref_token_123"),
            access_token="acc_token_456"
        )

    # 1. Auth URL
    auth_resp = await client.get("/api/gmail/auth-url")
    assert auth_resp.status_code == 200
    assert "auth_url" in auth_resp.json()

    # 2. Get me account
    me_resp = await client.get("/api/gmail/me")
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "dineshkumarsaj@gmail.com"


    # 3. Send email via API
    send_resp = await client.post("/api/gmail/send", json={
        "recipient_email": "operations@roots.co.in",
        "subject": "Benchmarking Research Invitation",
        "body": "Dear Operations Lead, we invite your team to participate in our study."
    })
    assert send_resp.status_code == 200
    msg_data = send_resp.json()
    assert msg_data["recipient_email"] == "operations@roots.co.in"
    assert msg_data["status"] == "SENT"
    message_id = msg_data["id"]

    # 4. Get message status
    status_resp = await client.get(f"/api/gmail/status/{message_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["id"] == message_id

    # 5. List messages
    list_resp = await client.get("/api/gmail/messages")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # 6. Schedule follow-up
    fu_resp = await client.post(f"/api/gmail/messages/{message_id}/follow-up", json={"follow_up_days": 3})
    assert fu_resp.status_code == 200
    assert fu_resp.json()["status"] == "FOLLOW_UP"
    assert fu_resp.json()["follow_up_count"] == 1

    # 7. Poll replies
    poll_resp = await client.post("/api/gmail/poll-replies")
    assert poll_resp.status_code == 200
    assert "checked_threads" in poll_resp.json()
