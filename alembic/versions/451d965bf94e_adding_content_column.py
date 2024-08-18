"""adding content column

Revision ID: 451d965bf94e
Revises: 125654e095ce
Create Date: 2024-08-18 16:19:59.316011

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "451d965bf94e"
down_revision: Union[str, None] = "125654e095ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass
