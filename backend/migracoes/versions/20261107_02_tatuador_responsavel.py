"""Adiciona o tatuador responsável à tatuagem.

A agenda é do tatuador, e a tatuagem precisa dizer de quem é a agenda. As
tatuagens que já existiam ficam com o primeiro tatuador do estúdio, que é o
responsável atual; uma tatuagem nova recebe o mesmo padrão no serviço e pode ser
reatribuída pelo administrador.

A coluna aceita NULL de propósito: um banco novo pode receber esta migration
antes de existir uma conta de tatuador. Nesse caso a agenda fica fechada até o
administrador cadastrar alguém e atribuir a tatuagem, em vez de a migration
falhar e impedir o sistema de subir.
"""

from alembic import op
import sqlalchemy as sa


revision = "20261107_02"
down_revision = "20261107_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a coluna, preenche as tatuagens existentes e liga a chave estrangeira."""
    op.add_column(
        "tatuagens",
        sa.Column("tatuador_id", sa.Integer(), nullable=True),
    )

    # O primeiro tatuador por id é o responsável que o estúdio já tinha na
    # prática. O UPDATE só toca nas linhas sem responsável, então rodar a
    # migration num banco que já tem atribuições não sobrescreve nada.
    op.execute(
        "UPDATE tatuagens SET tatuador_id = ("
        "SELECT u.id FROM usuarios AS u "
        "JOIN grupos AS g ON g.id = u.grupo_id "
        "WHERE g.codigo = 'tatuador' ORDER BY u.id LIMIT 1"
        ") WHERE tatuador_id IS NULL"
    )

    op.create_foreign_key(
        "fk_tatuagens_tatuador",
        "tatuagens",
        "usuarios",
        ["tatuador_id"],
        ["id"],
    )
    op.create_index(
        "ix_tatuagens_tatuador_id",
        "tatuagens",
        ["tatuador_id"],
    )


def downgrade() -> None:
    """Desfaz a coluna e o índice que a acompanha."""
    op.drop_index("ix_tatuagens_tatuador_id", table_name="tatuagens")
    op.drop_constraint(
        "fk_tatuagens_tatuador",
        "tatuagens",
        type_="foreignkey",
    )
    op.drop_column("tatuagens", "tatuador_id")
