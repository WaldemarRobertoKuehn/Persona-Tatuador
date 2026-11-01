"""Cria armazenamento de tokens temporários para redefinição de senha."""

from alembic import op
import sqlalchemy as sa


revision = "20261031_01"
down_revision = "20261021_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tokens_redefinicao_senha",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name="fk_tokens_redefinicao_usuario",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("usuario_id", name="uq_tokens_redefinicao_usuario"),
        sa.UniqueConstraint("token_hash", name="uq_tokens_redefinicao_hash"),
    )


def downgrade() -> None:
    op.drop_table("tokens_redefinicao_senha")
