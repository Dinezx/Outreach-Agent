"""create company business intelligence table

Revision ID: 20260807_0004
Revises: 20260806_0003
Create Date: 2026-08-07 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0004"
down_revision = "20260806_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company_business_intelligence",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("company_id", sa.String(length=36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("sub_industry", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("products", sa.JSON(), nullable=False),
        sa.Column("services", sa.JSON(), nullable=False),
        sa.Column("manufacturing_type", sa.String(length=255), nullable=True),
        sa.Column("departments", sa.JSON(), nullable=False),
        sa.Column("locations", sa.JSON(), nullable=False),
        sa.Column("certifications", sa.JSON(), nullable=False),
        sa.Column("markets", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("pain_points", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_company_business_intelligence_company_id", "company_business_intelligence", ["company_id"], unique=True)
    op.create_index("ix_company_business_intelligence_industry", "company_business_intelligence", ["industry"], unique=False)
    op.create_index("ix_company_business_intelligence_manufacturing_type", "company_business_intelligence", ["manufacturing_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_business_intelligence_manufacturing_type", table_name="company_business_intelligence")
    op.drop_index("ix_company_business_intelligence_industry", table_name="company_business_intelligence")
    op.drop_index("ix_company_business_intelligence_company_id", table_name="company_business_intelligence")
    op.drop_table("company_business_intelligence")
