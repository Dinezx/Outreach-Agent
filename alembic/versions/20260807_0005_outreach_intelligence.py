"""create outreach campaigns and history tables

Revision ID: 20260807_0005
Revises: 20260807_0004
Create Date: 2026-08-07 14:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0005"
down_revision = "20260807_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outreach_campaigns",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contact_id", sa.String(length=36), sa.ForeignKey("company_contacts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decision_maker_id", sa.String(length=36), sa.ForeignKey("decision_makers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("channel", sa.String(length=100), nullable=False, server_default="office_email"),
        sa.Column("target_role", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=True),
        sa.Column("email_body", sa.Text(), nullable=True),
        sa.Column("linkedin_message", sa.Text(), nullable=True),
        sa.Column("phone_script", sa.Text(), nullable=True),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("channel_confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("overall_confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING_APPROVAL"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("generation_time_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_campaigns_company_id", "outreach_campaigns", ["company_id"], unique=False)
    op.create_index("ix_outreach_campaigns_status", "outreach_campaigns", ["status"], unique=False)

    op.create_table(
        "outreach_history",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("campaign_id", sa.String(length=36), sa.ForeignKey("outreach_campaigns.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_history_campaign_id", "outreach_history", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_outreach_history_campaign_id", table_name="outreach_history")
    op.drop_table("outreach_history")

    op.drop_index("ix_outreach_campaigns_status", table_name="outreach_campaigns")
    op.drop_index("ix_outreach_campaigns_company_id", table_name="outreach_campaigns")
    op.drop_table("outreach_campaigns")
