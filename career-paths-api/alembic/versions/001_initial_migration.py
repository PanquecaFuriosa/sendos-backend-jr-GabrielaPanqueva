"""Initial migration with all tables

Revision ID: 001
Revises: 
Create Date: 2026-01-22 03:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('current_position', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('years_experience', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create evaluation_cycles table
    op.create_table('evaluation_cycles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'CLOSED', 'DRAFT', name='cyclestatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create competencies table
    op.create_table('competencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competencies_name'), 'competencies', ['name'], unique=True)
    
    # Create evaluations table
    op.create_table('evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluatee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cycle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluator_relationship', sa.Enum('SELF', 'MANAGER', 'PEER', 'DIRECT_REPORT', name='evaluatorrelationship'), nullable=False),
        sa.Column('general_feedback', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SUBMITTED', name='evaluationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['evaluation_cycles.id'], ),
        sa.ForeignKeyConstraint(['evaluatee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create evaluation_details table
    op.create_table('evaluation_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('competency_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['competency_id'], ['competencies.id'], ),
        sa.ForeignKeyConstraint(['evaluation_id'], ['evaluations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create assessments table
    op.create_table('assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cycle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scores_by_competency', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='processingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['evaluation_cycles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create career_paths table
    op.create_table('career_paths',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_role', sa.String(), nullable=True),
        sa.Column('target_role', sa.String(), nullable=True),
        sa.Column('estimated_timeline_months', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED', name='careerpathstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create career_path_steps table
    op.create_table('career_path_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('career_path_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('competencies_to_develop', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('estimated_duration_months', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['career_path_id'], ['career_paths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create development_actions table
    op.create_table('development_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('career_path_step_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['career_path_step_id'], ['career_path_steps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('development_actions')
    op.drop_table('career_path_steps')
    op.drop_table('career_paths')
    op.drop_table('assessments')
    op.drop_table('evaluation_details')
    op.drop_table('evaluations')
    op.drop_table('competencies')
    op.drop_table('evaluation_cycles')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='careerpathstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='processingstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='evaluationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='evaluatorrelationship').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='cyclestatus').drop(op.get_bind(), checkfirst=True)
