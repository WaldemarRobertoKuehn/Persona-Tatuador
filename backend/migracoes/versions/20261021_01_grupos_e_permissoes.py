"""NOVO: cria grupos persistentes e permissões para controlar rotas."""

from alembic import op
import sqlalchemy as sa


revision = "20261021_01"
down_revision = "ea09ccd9493f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """NOVO: cria o catálogo e migra os papéis atuais sem perder usuários."""
    op.create_table(
        "grupos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("nome", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo", name="uq_grupos_codigo"),
        sa.UniqueConstraint("nome", name="uq_grupos_nome"),
    )
    op.create_table(
        "permissoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("codigo", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=250), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo", name="uq_permissoes_codigo"),
    )
    op.create_table(
        "grupos_permissoes",
        sa.Column("grupo_id", sa.Integer(), nullable=False),
        sa.Column("permissao_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["grupo_id"],
            ["grupos.id"],
            name="fk_grupos_permissoes_grupo",
        ),
        sa.ForeignKeyConstraint(
            ["permissao_id"],
            ["permissoes.id"],
            name="fk_grupos_permissoes_permissao",
        ),
        sa.PrimaryKeyConstraint("grupo_id", "permissao_id"),
    )

    # NOVO: IDs explícitos deixam os vínculos iniciais reproduzíveis em qualquer banco.
    grupos = sa.table(
        "grupos",
        sa.column("id", sa.Integer()),
        sa.column("codigo", sa.String()),
        sa.column("nome", sa.String()),
    )
    op.bulk_insert(
        grupos,
        [
            {"id": 1, "codigo": "cliente", "nome": "Cliente"},
            {"id": 2, "codigo": "tatuador", "nome": "Tatuador"},
            {"id": 3, "codigo": "administrador", "nome": "Administrador"},
        ],
    )

    # NOVO: este catálogo é a lista de permissões de rota que os administradores
    # poderão conceder pela API. Os IDs são usados na tabela de associação abaixo.
    permissoes = sa.table(
        "permissoes",
        sa.column("id", sa.Integer()),
        sa.column("codigo", sa.String()),
        sa.column("descricao", sa.String()),
    )
    op.bulk_insert(
        permissoes,
        [
            {"id": 1, "codigo": "perfil:consultar_proprio", "descricao": "Consultar o próprio perfil."},
            {"id": 2, "codigo": "usuarios:consultar", "descricao": "Consultar dados de outros usuários."},
            {"id": 3, "codigo": "usuarios:atribuir_grupo", "descricao": "Atribuir um usuário a um grupo."},
            {"id": 4, "codigo": "tatuagens:criar", "descricao": "Solicitar ou criar tatuagens."},
            {"id": 5, "codigo": "tatuagens:criar_para_qualquer_cliente", "descricao": "Criar tatuagens para qualquer cliente."},
            {"id": 6, "codigo": "tatuagens:listar_proprias", "descricao": "Listar tatuagens próprias."},
            {"id": 7, "codigo": "tatuagens:listar_todas", "descricao": "Listar todas as tatuagens."},
            {"id": 8, "codigo": "tatuagens:consultar_propria", "descricao": "Consultar uma tatuagem própria."},
            {"id": 9, "codigo": "tatuagens:consultar_todas", "descricao": "Consultar qualquer tatuagem."},
            {"id": 10, "codigo": "passos:listar_proprios", "descricao": "Consultar passos de tatuagens próprias."},
            {"id": 11, "codigo": "passos:listar_todos", "descricao": "Consultar passos de qualquer tatuagem."},
            {"id": 12, "codigo": "passos:registrar_proprio", "descricao": "Registrar passos em tatuagens próprias."},
            {"id": 13, "codigo": "passos:registrar_todos", "descricao": "Registrar passos em qualquer tatuagem."},
            {"id": 14, "codigo": "grupos:consultar", "descricao": "Listar grupos e suas permissões."},
            {"id": 15, "codigo": "grupos:gerenciar", "descricao": "Criar grupos e alterar suas permissões."},
        ],
    )

    # NOVO: Cliente só recebe escopo próprio; Tatuador recebe o escopo do estúdio;
    # Administrador recebe o catálogo completo e as permissões de gestão.
    grupos_permissoes = sa.table(
        "grupos_permissoes",
        sa.column("grupo_id", sa.Integer()),
        sa.column("permissao_id", sa.Integer()),
    )
    op.bulk_insert(
        grupos_permissoes,
        [
            *(
                {"grupo_id": 1, "permissao_id": permissao_id}
                for permissao_id in [1, 2, 4, 6, 8, 10, 12]
            ),
            *(
                {"grupo_id": 2, "permissao_id": permissao_id}
                for permissao_id in [1, 2, 4, 5, 7, 9, 11, 13]
            ),
            *(
                {"grupo_id": 3, "permissao_id": permissao_id}
                for permissao_id in range(1, 16)
            ),
        ],
    )

    op.execute(
        "SELECT setval(pg_get_serial_sequence('grupos', 'id'), "
        "COALESCE((SELECT MAX(id) FROM grupos), 1), true)"
    )
    op.execute(
        "SELECT setval(pg_get_serial_sequence('permissoes', 'id'), "
        "COALESCE((SELECT MAX(id) FROM permissoes), 1), true)"
    )

    # NOVO: os usuários atuais mantêm os papéis existentes e passam a apontar para
    # os grupos equivalentes. A migration para com erro se encontrar papel inesperado.
    op.alter_column(
        "usuarios",
        "papel",
        existing_type=sa.String(length=20),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.add_column("usuarios", sa.Column("grupo_id", sa.Integer(), nullable=True))
    conexao = op.get_bind()
    papeis = conexao.execute(sa.text("SELECT DISTINCT papel FROM usuarios")).scalars()
    papeis_desconhecidos = sorted(set(papeis) - {"cliente", "tatuador", "administrador"})
    if papeis_desconhecidos:
        raise RuntimeError(
            "Há usuários com papéis sem grupo correspondente: "
            + ", ".join(papeis_desconhecidos)
        )
    conexao.execute(
        sa.text(
            "UPDATE usuarios AS u "
            "SET grupo_id = g.id "
            "FROM grupos AS g "
            "WHERE g.codigo = u.papel"
        )
    )
    op.alter_column("usuarios", "grupo_id", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_usuarios_grupo",
        "usuarios",
        "grupos",
        ["grupo_id"],
        ["id"],
    )


def downgrade() -> None:
    """NOVO: remove os vínculos antes das tabelas que os sustentam."""
    op.drop_constraint("fk_usuarios_grupo", "usuarios", type_="foreignkey")
    op.drop_column("usuarios", "grupo_id")
    op.drop_table("grupos_permissoes")
    op.drop_table("permissoes")
    op.drop_table("grupos")
