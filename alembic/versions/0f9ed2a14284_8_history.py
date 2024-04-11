"""8_history

Revision ID: 0f9ed2a14284
Revises: 473c2b722d39
Create Date: 2024-04-11 04:37:30.069197

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from app.contrib.history import EntityChoices, SubjectChoices

# revision identifiers, used by Alembic.
revision = '0f9ed2a14284'
down_revision = '473c2b722d39'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('a_i_history',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('entity', sqlalchemy_utils.types.choice.ChoiceType(
        choices=EntityChoices, impl=sa.String(50),
    ), nullable=False),
    sa.Column('subject_type', sqlalchemy_utils.types.choice.ChoiceType(
        choices=SubjectChoices, impl=sa.String(50)
    ), nullable=False),
    sa.Column('content', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fx_ai_history_user_id', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('a_i_history')
    # ### end Alembic commands ###
