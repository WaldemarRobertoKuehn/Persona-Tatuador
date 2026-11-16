"""Deixa o tatuador apenas com a continuidade da agenda.

O cliente escolhe e envia o desenho e aprova a arte. No atendimento presencial,
o administrador escolhe e autoriza. O tatuador não envia, não remove e não gera
imagens; ele segue com a agenda e os passos do atendimento.
"""

from alembic import op


revision = "20261115_03"
down_revision = "20261115_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove do grupo Tatuador as permissões de imagem e de geração."""
    op.execute(
        "DELETE FROM grupos_permissoes "
        "WHERE grupo_id = 2 AND permissao_id IN (16, 17, 23)"
    )


def downgrade() -> None:
    """Devolve ao tatuador as permissões que ele tinha antes."""
    op.execute(
        "INSERT INTO grupos_permissoes (grupo_id, permissao_id) "
        "VALUES (2, 16), (2, 17), (2, 23) ON CONFLICT DO NOTHING"
    )
