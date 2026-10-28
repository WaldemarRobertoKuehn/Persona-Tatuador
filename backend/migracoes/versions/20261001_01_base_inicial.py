"""Cria as tabelas originais do sistema.

Revision ID: 20261001_01
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20261001_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tatuagens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=False),
        sa.Column("ideia", sa.String(length=500), nullable=False),
        sa.Column("local_do_corpo", sa.String(length=80), nullable=False),
        sa.Column("tamanho", sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column("etapa", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name="fk_tatuagens_cliente",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "passos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tatuagem_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("observacao", sa.String(length=500), server_default=sa.text("''"), nullable=False),
        sa.ForeignKeyConstraint(
            ["tatuagem_id"],
            ["tatuagens.id"],
            name="fk_passos_tatuagem",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("passos")
    op.drop_table("tatuagens")
    op.drop_table("clientes")
