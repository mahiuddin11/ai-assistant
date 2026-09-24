"""create permissions and permission_audit_log tables

Revision ID: e79517bb3a1f
Revises: 472a5c0234fe
Create Date: 2026-09-25 01:22:17.215365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e79517bb3a1f'
down_revision: Union[str, Sequence[str], None] = '472a5c0234fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "permissions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),  # "granted" | "revoked"
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )

     # ইমিউটেবল audit log — এখানে কখনো UPDATE/DELETE হবে না, শুধু INSERT (append-only)
    op.create_table(
        "permission_audit_log",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),  # "grant" | "revoke" | "check_allowed" | "check_denied"
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("permission_audit_log")
    op.drop_table("permissions")
