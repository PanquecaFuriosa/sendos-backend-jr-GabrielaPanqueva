"""add_unique_constraint_evaluations

Revision ID: 17dc3ec226b5
Revises: 67146f95c453
Create Date: 2026-01-22 18:07:17.953115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17dc3ec226b5'
down_revision: Union[str, None] = '67146f95c453'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, delete duplicate evaluations keeping only the oldest one per combination
    op.execute("""
        DELETE FROM evaluations
        WHERE created_at NOT IN (
            SELECT MIN(created_at)
            FROM evaluations
            GROUP BY employee_id, evaluator_id, cycle_id, evaluator_relationship
        )
    """)
    
    # Add unique constraint
    op.create_unique_constraint(
        'unique_evaluation_per_relationship',
        'evaluations',
        ['employee_id', 'evaluator_id', 'cycle_id', 'evaluator_relationship']
    )


def downgrade() -> None:
    op.drop_constraint('unique_evaluation_per_relationship', 'evaluations', type_='unique')
