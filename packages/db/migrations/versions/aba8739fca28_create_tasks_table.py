"""create tasks table

Revision ID: aba8739fca28
Revises: e79517bb3a1f
Create Date: 2026-09-25 14:30:26.369172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aba8739fca28'
down_revision: Union[str, Sequence[str], None] = 'e79517bb3a1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tasks",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("conversation_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("task_type", sa.String(length=50), nullable=False),  # "chat_message" | "tool_call" ইত্যাদি
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),  # queued | running | completed | failed
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tasks")