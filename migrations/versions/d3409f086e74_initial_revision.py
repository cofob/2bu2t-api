"""Initial revision

Revision ID: d3409f086e74
Revises: 
Create Date: 2022-10-02 00:48:42.317992

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "d3409f086e74"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column("nickname", sqlmodel.sql.sqltypes.AutoString(length=16), nullable=False),
        sa.Column("disabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.Integer(), nullable=False),
        sa.Column("uuid", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_nickname"), "user", ["nickname"], unique=True)
    op.create_index(op.f("ix_user_uuid"), "user", ["uuid"], unique=True)
    op.create_table(
        "usertoken",
        sa.Column("uuid", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("expire_in", sa.Integer(), nullable=False),
        sa.Column("user", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user"],
            ["user.uuid"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index(op.f("ix_usertoken_uuid"), "usertoken", ["uuid"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_usertoken_uuid"), table_name="usertoken")
    op.drop_table("usertoken")
    op.drop_index(op.f("ix_user_uuid"), table_name="user")
    op.drop_index(op.f("ix_user_nickname"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    # ### end Alembic commands ###
