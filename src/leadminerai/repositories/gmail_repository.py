from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leadminerai.models.gmail import GmailAccount, GmailMessage


class GmailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_account(
        self,
        email: str,
        encrypted_refresh_token: str | None = None,
        access_token: str | None = None,
        token_expiry: datetime | None = None
    ) -> GmailAccount:
        stmt = select(GmailAccount).where(GmailAccount.email == email)
        res = await self.session.execute(stmt)
        account = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if not account:
            account = GmailAccount(
                email=email,
                encrypted_refresh_token=encrypted_refresh_token,
                access_token=access_token,
                token_expiry=token_expiry,
                is_active=True,
                created_at=now,
                updated_at=now
            )
            self.session.add(account)
        else:
            if encrypted_refresh_token:
                account.encrypted_refresh_token = encrypted_refresh_token
            if access_token:
                account.access_token = access_token
            if token_expiry:
                account.token_expiry = token_expiry
            account.is_active = True
            account.updated_at = now

        await self.session.commit()
        await self.session.refresh(account)
        return account

    async def get_active_account(self) -> GmailAccount | None:
        stmt = (
            select(GmailAccount)
            .where(GmailAccount.is_active == True)
            .order_by(GmailAccount.updated_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_message(self, data: dict) -> GmailMessage:
        now = datetime.now(timezone.utc)
        msg = GmailMessage(
            company_id=data.get("company_id"),
            contact_id=data.get("contact_id"),
            decision_maker_id=data.get("decision_maker_id"),
            campaign_id=data.get("campaign_id"),
            gmail_account_id=data.get("gmail_account_id"),
            gmail_message_id=data.get("gmail_message_id"),
            thread_id=data.get("thread_id"),
            history_id=data.get("history_id"),
            subject=data.get("subject"),
            body=data.get("body"),
            recipient_email=data.get("recipient_email"),
            sender_email=data.get("sender_email"),
            status=data.get("status", "DRAFT"),
            follow_up_count=data.get("follow_up_count", 0),
            created_at=now,
            updated_at=now
        )
        self.session.add(msg)
        await self.session.commit()
        return await self.get_message_by_id(msg.id)  # type: ignore

    async def get_message_by_id(self, message_id: str) -> GmailMessage | None:
        stmt = (
            select(GmailMessage)
            .options(
                selectinload(GmailMessage.company),
                selectinload(GmailMessage.contact),
                selectinload(GmailMessage.decision_maker),
                selectinload(GmailMessage.campaign),
                selectinload(GmailMessage.account)
            )
            .where(GmailMessage.id == message_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_message_status(
        self,
        message_id: str,
        status: str,
        sent_at: datetime | None = None,
        gmail_msg_id: str | None = None,
        thread_id: str | None = None,
        history_id: str | None = None
    ) -> GmailMessage:
        msg = await self.get_message_by_id(message_id)
        if not msg:
            raise ValueError(f"GmailMessage {message_id} not found")

        now = datetime.now(timezone.utc)
        msg.status = status
        msg.updated_at = now

        if sent_at:
            msg.sent_at = sent_at
        if gmail_msg_id:
            msg.gmail_message_id = gmail_msg_id
        if thread_id:
            msg.thread_id = thread_id
        if history_id:
            msg.history_id = history_id

        await self.session.commit()
        self.session.expire_all()
        return await self.get_message_by_id(message_id)  # type: ignore

    async def record_reply(
        self,
        message_id: str,
        reply_from: str,
        reply_body: str,
        replied_at: datetime | None = None
    ) -> GmailMessage:
        msg = await self.get_message_by_id(message_id)
        if not msg:
            raise ValueError(f"GmailMessage {message_id} not found")

        now = datetime.now(timezone.utc)
        msg.status = "REPLIED"
        msg.is_reply = True
        msg.reply_from = reply_from
        msg.reply_body = reply_body
        msg.replied_at = replied_at or now
        msg.updated_at = now

        await self.session.commit()
        self.session.expire_all()
        return await self.get_message_by_id(message_id)  # type: ignore

    async def schedule_follow_up(
        self,
        message_id: str,
        days: int = 3
    ) -> GmailMessage:
        msg = await self.get_message_by_id(message_id)
        if not msg:
            raise ValueError(f"GmailMessage {message_id} not found")

        now = datetime.now(timezone.utc)
        msg.status = "FOLLOW_UP"
        msg.follow_up_count += 1
        msg.scheduled_follow_up_at = now + timedelta(days=days)
        msg.updated_at = now

        await self.session.commit()
        self.session.expire_all()
        return await self.get_message_by_id(message_id)  # type: ignore

    async def list_messages(
        self,
        company_id: str | None = None,
        recipient_email: str | None = None,
        status: str | None = None,
        thread_id: str | None = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[list[GmailMessage], int]:
        stmt = (
            select(GmailMessage)
            .options(
                selectinload(GmailMessage.company),
                selectinload(GmailMessage.contact),
                selectinload(GmailMessage.decision_maker),
                selectinload(GmailMessage.campaign),
                selectinload(GmailMessage.account)
            )
            .order_by(GmailMessage.created_at.desc())
        )
        count_stmt = select(func.count()).select_from(GmailMessage)

        if company_id:
            stmt = stmt.where(GmailMessage.company_id == company_id)
            count_stmt = count_stmt.where(GmailMessage.company_id == company_id)
        if recipient_email:
            stmt = stmt.where(GmailMessage.recipient_email == recipient_email)
            count_stmt = count_stmt.where(GmailMessage.recipient_email == recipient_email)
        if status:
            stmt = stmt.where(GmailMessage.status == status)
            count_stmt = count_stmt.where(GmailMessage.status == status)
        if thread_id:
            stmt = stmt.where(GmailMessage.thread_id == thread_id)
            count_stmt = count_stmt.where(GmailMessage.thread_id == thread_id)

        total_res = await self.session.scalar(count_stmt)
        total = int(total_res or 0)

        res = await self.session.execute(stmt.offset(skip).limit(limit))
        items = list(res.scalars().all())
        return items, total
