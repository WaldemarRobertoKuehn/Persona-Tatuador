"""Adiciona os campos temporários usados na redefinição de senha."""

from alembic import op
import sqlalchemy as sa


revision = "20261106_01"
down_revision = "20261021_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Guarda somente o hash e os horários necessários para o token temporário."""
    op.add_column(
        "usuarios",
        sa.Column("token_redefinicao_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "token_redefinicao_expira_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "usuarios",
        sa.Column(
            "token_redefinicao_solicitado_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove os campos de redefinição sem alterar as credenciais existentes."""
    op.drop_column("usuarios", "token_redefinicao_solicitado_em")
    op.drop_column("usuarios", "token_redefinicao_expira_em")
    op.drop_column("usuarios", "token_redefinicao_hash")