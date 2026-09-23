"""add external identity to users

Revision ID: 269c8b809978
Revises: 2075d4bbc353
Create Date: 2026-09-23 03:05:13.206365

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "269c8b809978"
down_revision: str | Sequence[str] | None = "2075d4bbc353"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("entra_issuer", sa.String(length=255), nullable=True)
    )
    op.add_column("users", sa.Column("entra_sub", sa.String(length=255), nullable=True))
    op.create_unique_constraint(
        "uq_users_entra_identity", "users", ["entra_issuer", "entra_sub"]
    )
    # 本人の判定は(entra_issuer, entra_sub)で行う。
    # APIに届くアクセストークンにemailは含まれず値が入らないため削除する
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.drop_column("users", "email")


def downgrade() -> None:
    """Downgrade schema.

    削除したemailの値は復元できない。元はNOT NULLだったが、戻す値が無いため
    NULL可で列だけを戻す。
    """
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.drop_constraint("uq_users_entra_identity", "users", type_="unique")
    op.drop_column("users", "entra_sub")
    op.drop_column("users", "entra_issuer")
