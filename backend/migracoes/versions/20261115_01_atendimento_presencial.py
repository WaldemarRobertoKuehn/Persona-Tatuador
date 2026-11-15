"""Adiciona a origem do pedido e as permissões do atendimento presencial.

A coluna origem separa o pedido feito pelo site do pedido cadastrado no balcão.
É essa marca que autoriza o administrador a aprovar o desenho em nome de uma
cliente sem conta. As permissões novas liberam o cadastro de clientes e a geração
de desenho por IA sem abrir essas rotas para os outros grupos.
"""

from alembic import op
import sqlalchemy as sa


revision = "20261115_01"
down_revision = "20261109_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria a origem e entrega as permissões novas aos grupos certos."""
    op.add_column(
        "tatuagens",
        sa.Column(
            "origem",
            sa.String(length=20),
            server_default=sa.text("'cliente'"),
            nullable=False,
        ),
    )

    permissoes = sa.table(
        "permissoes",
        sa.column("id", sa.Integer()),
        sa.column("codigo", sa.String()),
        sa.column("descricao", sa.String()),
    )
    op.bulk_insert(
        permissoes,
        [
            {
                "id": 21,
                "codigo": "clientes:consultar",
                "descricao": "Consultar as clientes do estúdio.",
            },
            {
                "id": 22,
                "codigo": "clientes:cadastrar",
                "descricao": "Cadastrar clientes no atendimento presencial.",
            },
            {
                "id": 23,
                "codigo": "desenhos:gerar",
                "descricao": "Gerar propostas de desenho com IA.",
            },
        ],
    )

    grupos_permissoes = sa.table(
        "grupos_permissoes",
        sa.column("grupo_id", sa.Integer()),
        sa.column("permissao_id", sa.Integer()),
    )
    vinculos = [
        # O tatuador pode gerar a proposta, mas não cadastrar cliente nem
        # aprovar em nome da cliente.
        {"grupo_id": 2, "permissao_id": 23},
    ]
    # O administrador conduz o atendimento presencial inteiro.
    vinculos.extend(
        {"grupo_id": 3, "permissao_id": permissao_id}
        for permissao_id in [21, 22, 23]
    )
    op.bulk_insert(grupos_permissoes, vinculos)

    op.execute(
        "SELECT setval(pg_get_serial_sequence('permissoes', 'id'), "
        "COALESCE((SELECT MAX(id) FROM permissoes), 1), true)"
    )


def downgrade() -> None:
    """Remove as permissões novas e depois a coluna que elas usam."""
    codigos = "'clientes:consultar', 'clientes:cadastrar', 'desenhos:gerar'"
    op.execute(
        "DELETE FROM grupos_permissoes WHERE permissao_id IN ("
        f"SELECT id FROM permissoes WHERE codigo IN ({codigos})"
        ")"
    )
    op.execute(f"DELETE FROM permissoes WHERE codigo IN ({codigos})")
    op.drop_column("tatuagens", "origem")
