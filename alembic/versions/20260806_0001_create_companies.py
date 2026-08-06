"""create companies table

Revision ID: 20260806_0001
Revises: 
Create Date: 2026-08-06 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "20260806_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("website_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "FOUND", "NOT_FOUND", "FAILED", name="company_status", native_enum=False),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_companies_name"), "companies", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_name"), table_name="companies")
    op.drop_table("companies")
