"""rename report table

Revision ID: 3e88b86c020a
Revises: dff672788f93
Create Date: 2024-03-03 00:15:08.971814

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e88b86c020a'
down_revision = 'dff672788f93'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('reportparams', 'reportparameter')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('reportparameter', 'reportparams')
    # ### end Alembic commands ###
