"""token_hash column type srt to bytes

Revision ID: 659a59338ce7
Revises: 35839628629c
Create Date: 2026-02-03 00:51:23.455612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '659a59338ce7'
down_revision: Union[str, Sequence[str], None] = '35839628629c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            ALTER TABLE user_sessions
            ALTER COLUMN token_hash
            TYPE BYTEA
            USING token_hash::bytea
        """)


def downgrade() -> None:
    op.execute("""
           ALTER TABLE user_sessions
           ALTER COLUMN token_hash
           TYPE VARCHAR(60)
           USING token_hash::text
       """)
