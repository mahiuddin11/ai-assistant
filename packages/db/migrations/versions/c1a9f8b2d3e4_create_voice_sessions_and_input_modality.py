"""create voice sessions table and add input modality to sessions

Revision ID: c1a9f8b2d3e4
Revises: aba8739fca28
Create Date: 2026-10-07 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c1a9f8b2d3e4'
down_revision: Union[str, Sequence[str], None] = 'aba8739fca28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "voice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("device_id", sa.String(length=255), nullable=False),
        sa.Column("speaker_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "sessions",
        sa.Column("input_modality", sa.String(length=20), server_default="text", nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("sessions", "input_modality")
    op.drop_table("voice_sessions")
