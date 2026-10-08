"""Adiciona email e hash de senha às contas já existentes."""

from alembic import op
import sqlalchemy as sa


revision = "20261007_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clientes", sa.Column("email", sa.String(length=254), nullable=True))
    op.add_column("clientes", sa.Column("senha_hash", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_clientes_email", "clientes", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_clientes_email", "clientes", type_="unique")
    op.drop_column("clientes", "senha_hash")
    op.drop_column("clientes", "email")
