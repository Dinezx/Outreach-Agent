"""create gmail accounts and messages tables

Revision ID: 20260807_0006
Revises: 20260807_0005
Create Date: 2026-08-07 16:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0006"
down_revision = "20260807_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gmail_accounts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_gmail_accounts_email", "gmail_accounts", ["email"], unique=True)

    op.create_table(
        "gmail_messages",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contact_id", sa.String(length=36), sa.ForeignKey("company_contacts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decision_maker_id", sa.String(length=36), sa.ForeignKey("decision_makers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("campaign_id", sa.String(length=36), sa.ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("gmail_account_id", sa.String(length=36), sa.ForeignKey("gmail_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("gmail_message_id", sa.String(length=255), nullable=True),
        sa.Column("thread_id", sa.String(length=255), nullable=True),
        sa.Column("history_id", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("recipient_email", sa.String(length=255), nullable=True),
        sa.Column("sender_email", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="DRAFT"),
        sa.Column("is_reply", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("reply_from", sa.String(length=255), nullable=True),
        sa.Column("reply_body", sa.Text(), nullable=True),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("follow_up_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("scheduled_follow_up_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_gmail_messages_gmail_message_id", "gmail_messages", ["gmail_message_id"], unique=False)
    op.create_index("ix_gmail_messages_thread_id", "gmail_messages", ["thread_id"], unique=False)
    op.create_index("ix_gmail_messages_recipient_email", "gmail_messages", ["recipient_email"], unique=False)
    op.create_index("ix_gmail_messages_status", "gmail_messages", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gmail_messages_status", table_name="gmail_messages")
    op.drop_index("ix_gmail_messages_recipient_email", table_name="gmail_messages")
    op.drop_index("ix_gmail_messages_thread_id", table_name="gmail_messages")
    op.drop_index("ix_gmail_messages_gmail_message_id", table_name="gmail_messages")
    op.drop_table("gmail_messages")

    op.drop_index("ix_gmail_accounts_email", table_name="gmail_accounts")
    op.drop_table("gmail_accounts")
