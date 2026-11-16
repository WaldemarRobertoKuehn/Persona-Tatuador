"""Dá ao cliente a opção de remover a imagem que ele recusou.

A aprovação e a recusa continuam sendo do cliente. Depois de recusar, ele pode
apagar o desenho recusado sem depender do tatuador. O tatuador não recebe a
permissão de aprovar: ela é removida do grupo dele caso tenha sido concedida
manualmente em algum banco.
"""

from alembic import op
import sqlalchemy as sa


revision = "20261115_02"
down_revision = "20261115_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Vincula a remoção de imagem ao cliente e tira a aprovação do tatuador."""
    grupos_permissoes = sa.table(
        "grupos_permissoes",
        sa.column("grupo_id", sa.Integer()),
        sa.column("permissao_id", sa.Integer()),
    )

    op.bulk_insert(
        grupos_permissoes,
        [{"grupo_id": 1, "permissao_id": 17}],
    )

    op.execute(
        "DELETE FROM grupos_permissoes "
        "WHERE grupo_id = 2 AND permissao_id = 18"
    )


def downgrade() -> None:
    """Desfaz o vínculo novo e devolve a aprovação ao tatuador."""
    op.execute(
        "DELETE FROM grupos_permissoes "
        "WHERE grupo_id = 1 AND permissao_id = 17"
    )
    op.execute(
        "INSERT INTO grupos_permissoes (grupo_id, permissao_id) "
        "VALUES (2, 18) ON CONFLICT DO NOTHING"
    )
