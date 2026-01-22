"""add_updated_at_to_career_path_steps

Revision ID: cbad3e563240
Revises: 6c9c56c32312
Create Date: 2026-01-22 02:03:14.562716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbad3e563240'
down_revision: Union[str, None] = '6c9c56c32312'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at column to career_path_steps
    op.add_column('career_path_steps', 
                  sa.Column('updated_at', sa.DateTime(), 
                           nullable=True,
                           server_default=sa.text('CURRENT_TIMESTAMP')))
    
    # Update existing rows
    op.execute("UPDATE career_path_steps SET updated_at = created_at WHERE updated_at IS NULL")
    
    # Make column non-nullable
    op.alter_column('career_path_steps', 'updated_at', nullable=False)


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column('career_path_steps', 'updated_at')
