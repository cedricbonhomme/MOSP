"""added is_locked attribute to object

Revision ID: 88304952e3ff
Revises: 257faccd2b4f
Create Date: 2021-08-16 12:20:50.169850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "88304952e3ff"
down_revision = "257faccd2b4f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "json_object",
        sa.Column(
            "is_locked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.schema.DefaultClause("False"),
        ),
    )
    op.alter_column(
        "json_object", "creator_id", existing_type=sa.INTEGER(), nullable=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "json_object", "creator_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.drop_column("json_object", "is_locked")
    # ### end Alembic commands ###
