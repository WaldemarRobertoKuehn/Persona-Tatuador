"""Adiciona o identificador curto de login, opcional para contas antigas.

O login passa a aceitar o e-mail ou este usuário. As contas novas escolhem o
usuário no cadastro; as que já existem ficam com a coluna vazia e podem definir
o usuário depois, pela tela da conta. O índice único permite vários NULL, mas
não dois usuários iguais.
"""

from alembic import op
import sqlalchemy as sa


revision = "20261109_01"
down_revision = "20261107_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a coluna opcional e o índice que impede usuários repetidos."""
    op.add_column(
        "usuarios",
        sa.Column("usuario", sa.String(length=50), nullable=True),
    )
    op.create_unique_constraint(
        "uq_usuarios_usuario",
        "usuarios",
        ["usuario"],
    )


def downgrade() -> None:
    """Remove o identificador sem alterar o e-mail nem a senha da conta."""
    op.drop_constraint(
        "uq_usuarios_usuario",
        "usuarios",
        type_="unique",
    )
    op.drop_column("usuarios", "usuario")
