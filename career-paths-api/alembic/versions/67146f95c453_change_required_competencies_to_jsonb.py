"""change_required_competencies_to_jsonb

Revision ID: 67146f95c453
Revises: cbad3e563240
Create Date: 2026-01-22 02:06:24.019756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '67146f95c453'
down_revision: Union[str, None] = 'cbad3e563240'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change required_competencies from ARRAY to JSONB
    # Use USING clause to convert array to JSONB
    op.execute("""
        ALTER TABLE career_path_steps 
        ALTER COLUMN required_competencies TYPE JSONB 
        USING to_jsonb(required_competencies)
    """)


def downgrade() -> None:
    # Revert JSONB to ARRAY
    op.execute("""
        ALTER TABLE career_path_steps 
        ALTER COLUMN required_competencies TYPE VARCHAR[] 
        USING CASE 
            WHEN jsonb_typeof(required_competencies) = 'array' 
            THEN ARRAY(SELECT jsonb_array_elements_text(required_competencies))
            ELSE NULL
        END
    """)
