"""2_chat

Revision ID: 394854b45131
Revises: 0238ee6479cd
Create Date: 2024-03-17 16:53:19.556494

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '394854b45131'
down_revision = '0238ee6479cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'chat_favorite',
        sa.Column('question', sa.String(length=255), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_favorite_id'), 'chat_favorite', ['id'], unique=False)
    op.create_table(
        'chat_history',
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('chat_data', sa.JSON(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.drop_table('chat_history')
    op.drop_index(op.f('ix_chat_favorite_id'), table_name='chat_favorite')
    op.drop_table('chat_favorite')
    # ### end Alembic commands ###
