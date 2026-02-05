"""rework tables

Revision ID: fa3163ab7c97
Revises: 659a59338ce7
Create Date: 2026-02-04 00:27:43.895401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'fa3163ab7c97'
down_revision: Union[str, Sequence[str], None] = '659a59338ce7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('publication', 'post')
    op.rename_table('publication_like', 'post_likes')
    op.alter_column('post', 'publication_id', new_column_name='post_id')
    op.alter_column('post_likes', 'publication_id', new_column_name='post_id')
    op.drop_index('ix_publication_like_publication_id', table_name='post_likes')
    op.create_index(op.f('ix_post_likes_post_id'), 'post_likes', ['post_id'], unique=False)
    op.drop_column('user_sessions', 'ip_address')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('user_sessions', sa.Column('ip_address', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.create_table('publication_like',
    sa.Column('like_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('publication_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['publication_id'], ['publication.publication_id'], name=op.f('publication_like_publication_id_fkey')),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.user_id'], name=op.f('publication_like_user_id_fkey')),
    sa.PrimaryKeyConstraint('like_id', name=op.f('publication_like_pkey')),
    sa.UniqueConstraint('publication_id', 'user_id', name=op.f('publication_like_publication_id_user_id_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_publication_like_publication_id'), 'publication_like', ['publication_id'], unique=False)
    op.create_table('publication',
    sa.Column('publication_id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.user_id'], name=op.f('publication_user_id_fkey')),
    sa.PrimaryKeyConstraint('publication_id', name=op.f('publication_pkey'))
    )
    op.drop_index(op.f('ix_post_likes_post_id'), table_name='post_likes')
    op.drop_table('post_likes')
    op.drop_table('post')
