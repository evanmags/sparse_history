"""rename history to revision

Revision ID: 7e0f9498063f
Revises: 
Create Date: 2024-02-23 19:00:56.202635

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e0f9498063f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("users", "user_revisions")
    op.alter_column("user_revisions", "id", new_column_name="revision_id")
    op.alter_column("user_revisions", "created_at", new_column_name="revised_at")


def downgrade() -> None:
    op.rename_table("user_revisions", "users")
    op.alter_column("users", "revision_id", new_column_name="id")
    op.alter_column("users", "revised_at", new_column_name="created_at")
