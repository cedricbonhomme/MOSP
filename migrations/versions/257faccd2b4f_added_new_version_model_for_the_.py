"""added new version model for the versioning of objects

Revision ID: 257faccd2b4f
Revises: 55ca2e7bf69a
Create Date: 2021-06-15 10:27:08.522480

"""
from alembic import op
import sqlalchemy as sa
from  sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '257faccd2b4f'
down_revision = '55ca2e7bf69a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "version",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column('version', sa.Column('creator_id', sa.Integer(), nullable=False))
    op.add_column('version', sa.Column('description', sa.Text(), nullable=False))
    op.add_column('version', sa.Column('json_object', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('version', sa.Column('last_updated', sa.DateTime(), nullable=True))
    op.add_column('version', sa.Column('name', sa.Text(), nullable=False))
    op.add_column('version', sa.Column('object_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'version', 'user', ['creator_id'], ['id'])
    op.create_foreign_key(None, 'version', 'json_object', ['object_id'], ['id'])


def downgrade():
    op.drop_table("version")