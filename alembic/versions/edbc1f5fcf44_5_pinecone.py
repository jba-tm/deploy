"""5_pinecone

Revision ID: edbc1f5fcf44
Revises: e516a16c73a8
Create Date: 2024-04-21 02:13:42.016079

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from app.contrib.pinecone import FileInfoStatusChoices

# revision identifiers, used by Alembic.
revision = 'edbc1f5fcf44'
down_revision = 'e516a16c73a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pinecone_api_info',
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('env', sa.String(length=255), nullable=False),
                    sa.Column('key', sa.String(length=255), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                              nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fx_pai_user_id', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table(
        'file_info',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file', sa.Text(), nullable=False),
        sa.Column('pinecone_id', sa.Integer(), nullable=False),
        sa.Column('status', sqlalchemy_utils.types.choice.ChoiceType(
            choices=FileInfoStatusChoices, impl=sa.String(25)
        ), nullable=False, default=FileInfoStatusChoices.PENDING ),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(['pinecone_id'], ['pinecone_api_info.id'], name='fx_file_info_pai_id',
                                ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fx_file_info_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('file_info')
    op.drop_table('pinecone_api_info')
    # ### end Alembic commands ###
