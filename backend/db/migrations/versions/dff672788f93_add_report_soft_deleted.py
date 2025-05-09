"""add report soft deleted

Revision ID: dff672788f93
Revises: d9469310a5a6
Create Date: 2024-02-23 13:54:38.479168

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dff672788f93'
down_revision = 'd9469310a5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('report',
                  sa.Column('soft_deleted', sa.Boolean(), default=False, server_default=str(False), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('report', 'soft_deleted')
    # ### end Alembic commands ###
