"""update_career_paths_table

Revision ID: 6c9c56c32312
Revises: 6e9d0b3b909e
Create Date: 2026-01-22 01:04:12.719368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c9c56c32312'
down_revision: Union[str, None] = '6e9d0b3b909e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Update career_paths table ===
    # Drop old columns
    op.drop_column('career_paths', 'assessment_id')
    op.drop_column('career_paths', 'current_role')
    op.drop_column('career_paths', 'target_role')
    op.drop_column('career_paths', 'estimated_timeline_months')
    
    # Add new columns
    op.add_column('career_paths', sa.Column('path_name', sa.String(), nullable=False, server_default='Unnamed Path'))
    op.add_column('career_paths', sa.Column('recommended', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('career_paths', sa.Column('total_duration_months', sa.Float(), nullable=False, server_default='12'))
    op.add_column('career_paths', sa.Column('feasibility_score', sa.Float(), nullable=True))
    op.add_column('career_paths', sa.Column('generated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')))
    op.add_column('career_paths', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('career_paths', sa.Column('completed_at', sa.DateTime(), nullable=True))
    
    # Update status column to new enum
    op.execute("ALTER TYPE careerpathstatus RENAME TO careerpathstatus_old")
    op.execute("CREATE TYPE careerpathstatus AS ENUM ('GENERATED', 'IN_PROGRESS', 'COMPLETED', 'ARCHIVED')")
    op.execute("ALTER TABLE career_paths ALTER COLUMN status TYPE careerpathstatus USING 'GENERATED'::careerpathstatus")
    op.execute("DROP TYPE careerpathstatus_old")
    
    # Remove server defaults
    op.alter_column('career_paths', 'path_name', server_default=None)
    op.alter_column('career_paths', 'recommended', server_default=None)
    op.alter_column('career_paths', 'total_duration_months', server_default=None)
    op.alter_column('career_paths', 'generated_at', server_default=None)
    
    # Add index
    op.create_index(op.f('ix_career_paths_user_id'), 'career_paths', ['user_id'], unique=False)
    
    # === Update career_path_steps table ===
    op.alter_column('career_path_steps', 'step_number', new_column_name='step_order')
    op.alter_column('career_path_steps', 'description', new_column_name='title')
    op.alter_column('career_path_steps', 'competencies_to_develop', new_column_name='required_competencies')
    op.alter_column('career_path_steps', 'estimated_duration_months', new_column_name='duration_months')
    op.add_column('career_path_steps', sa.Column('target_role', sa.String(), nullable=True))
    
    # === Update development_actions table ===
    op.alter_column('development_actions', 'career_path_step_id', new_column_name='step_id')
    op.alter_column('development_actions', 'action_type', new_column_name='type')
    op.drop_column('development_actions', 'priority')


def downgrade() -> None:
    # === Revert development_actions ===
    op.add_column('development_actions', sa.Column('priority', sa.String(), nullable=True))
    op.alter_column('development_actions', 'type', new_column_name='action_type')
    op.alter_column('development_actions', 'step_id', new_column_name='career_path_step_id')
    
    # === Revert career_path_steps ===
    op.drop_column('career_path_steps', 'target_role')
    op.alter_column('career_path_steps', 'duration_months', new_column_name='estimated_duration_months')
    op.alter_column('career_path_steps', 'required_competencies', new_column_name='competencies_to_develop')
    op.alter_column('career_path_steps', 'title', new_column_name='description')
    op.alter_column('career_path_steps', 'step_order', new_column_name='step_number')
    
    # === Revert career_paths ===
    op.drop_index(op.f('ix_career_paths_user_id'), table_name='career_paths')
    op.drop_column('career_paths', 'completed_at')
    op.drop_column('career_paths', 'started_at')
    op.drop_column('career_paths', 'generated_at')
    op.drop_column('career_paths', 'feasibility_score')
    op.drop_column('career_paths', 'total_duration_months')
    op.drop_column('career_paths', 'recommended')
    op.drop_column('career_paths', 'path_name')
    
    # Restore old columns
    op.add_column('career_paths', sa.Column('estimated_timeline_months', sa.Integer(), nullable=True))
    op.add_column('career_paths', sa.Column('target_role', sa.String(), nullable=True))
    op.add_column('career_paths', sa.Column('current_role', sa.String(), nullable=True))
    op.add_column('career_paths', sa.Column('assessment_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False))
    
    # Restore old enum
    op.execute("DROP TYPE careerpathstatus CASCADE")
    op.execute("CREATE TYPE careerpathstatus AS ENUM ('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED')")
    op.execute("ALTER TABLE career_paths ALTER COLUMN status TYPE careerpathstatus USING status::text::careerpathstatus")
