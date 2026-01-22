"""update_assessments_table

Revision ID: 6e9d0b3b909e
Revises: 001
Create Date: 2026-01-22 00:57:11.090685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e9d0b3b909e'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old column
    op.drop_column('assessments', 'scores_by_competency')
    
    # Rename status column to processing_status
    op.alter_column('assessments', 'status', new_column_name='processing_status')
    
    # Update enum type
    op.execute("ALTER TYPE processingstatus RENAME TO processingstatus_old")
    op.execute("CREATE TYPE processingstatus AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')")
    op.execute("ALTER TABLE assessments ALTER COLUMN processing_status TYPE processingstatus USING processing_status::text::processingstatus")
    op.execute("DROP TYPE processingstatus_old")
    
    # Add new columns
    op.add_column('assessments', sa.Column('ai_profile', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('assessments', sa.Column('processing_started_at', sa.DateTime(), nullable=True))
    op.add_column('assessments', sa.Column('processing_completed_at', sa.DateTime(), nullable=True))
    op.add_column('assessments', sa.Column('error_message', sa.String(), nullable=True))
    
    # Add indexes
    op.create_index(op.f('ix_assessments_user_id'), 'assessments', ['user_id'], unique=False)
    op.create_index(op.f('ix_assessments_cycle_id'), 'assessments', ['cycle_id'], unique=False)
    
    # Add unique constraint
    op.create_unique_constraint('uq_assessment_user_cycle', 'assessments', ['user_id', 'cycle_id'])


def downgrade() -> None:
    # Drop new columns and constraints
    op.drop_constraint('uq_assessment_user_cycle', 'assessments', type_='unique')
    op.drop_index(op.f('ix_assessments_cycle_id'), table_name='assessments')
    op.drop_index(op.f('ix_assessments_user_id'), table_name='assessments')
    op.drop_column('assessments', 'error_message')
    op.drop_column('assessments', 'processing_completed_at')
    op.drop_column('assessments', 'processing_started_at')
    op.drop_column('assessments', 'ai_profile')
    
    # Restore old enum
    op.execute("ALTER TYPE processingstatus RENAME TO processingstatus_old")
    op.execute("CREATE TYPE processingstatus AS ENUM ('PENDING', 'COMPLETED', 'FAILED')")
    op.execute("ALTER TABLE assessments ALTER COLUMN status TYPE processingstatus USING status::text::processingstatus")
    op.execute("DROP TYPE processingstatus_old")
    
    # Add back old column
    op.add_column('assessments', sa.Column('scores_by_competency', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True))
