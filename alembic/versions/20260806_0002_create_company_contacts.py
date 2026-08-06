"""create company_contacts table

Revision ID: 20260806_0002
Revises: 20260806_0001
Create Date: 2026-08-06 01:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260806_0002"
down_revision = "20260806_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_contacts",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=1024), nullable=True),
        sa.Column("phone", sa.String(length=255), nullable=True),
        sa.Column("mobile", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=255), nullable=True),
        sa.Column("linkedin", sa.String(length=1024), nullable=True),
        sa.Column("facebook", sa.String(length=1024), nullable=True),
        sa.Column("instagram", sa.String(length=1024), nullable=True),
        sa.Column("youtube", sa.String(length=1024), nullable=True),
        sa.Column("contact_page", sa.String(length=1024), nullable=True),
        sa.Column("maps_url", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_company_contacts_company_id"), "company_contacts", ["company_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_company_contacts_company_id"), table_name="company_contacts")
    op.drop_table("company_contacts")
