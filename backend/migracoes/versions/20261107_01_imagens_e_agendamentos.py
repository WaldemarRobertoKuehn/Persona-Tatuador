"""Cria imagens de tatuagem, agendamentos e as permissões novas.

As imagens ficam no PostgreSQL (BYTEA), então a migration não cria bucket nem
depende de serviço externo. Os agendamentos usam um índice único parcial para
bloquear o mesmo horário do mesmo tatuador somente enquanto o agendamento está
ativo.
"""

from alembic import op
import sqlalchemy as sa


revision = "20261107_01"
down_revision = "20261106_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria as tabelas e entrega as permissões aos grupos existentes."""
    op.create_table(
        "tatuagem_imagens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tatuagem_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "tipo",
            sa.String(length=20),
            server_default=sa.text("'desenho'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pendente'"),
            nullable=False,
        ),
        sa.Column("conteudo", sa.LargeBinary(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("aprovada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recusada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo_recusa", sa.String(length=500), nullable=True),
        sa.Column("aprovada_por_usuario_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tatuagem_id"],
            ["tatuagens.id"],
            name="fk_tatuagem_imagens_tatuagem",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["aprovada_por_usuario_id"],
            ["usuarios.id"],
            name="fk_tatuagem_imagens_aprovador",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agendamentos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tatuagem_id", sa.Integer(), nullable=False),
        sa.Column("tatuador_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("hora_inicio", sa.Time(), nullable=False),
        sa.Column("hora_fim", sa.Time(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'agendado'"),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tatuagem_id"],
            ["tatuagens.id"],
            name="fk_agendamentos_tatuagem",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tatuador_id"],
            ["usuarios.id"],
            name="fk_agendamentos_tatuador",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_agendamentos_tatuador_horario",
        "agendamentos",
        ["tatuador_id", "data", "hora_inicio"],
        unique=True,
        postgresql_where=sa.text("status = 'agendado'"),
    )

    # As permissões novas entram com IDs explícitos para os vínculos abaixo
    # serem reproduzíveis em qualquer banco que receba esta migration.
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
                "id": 16,
                "codigo": "imagens:enviar",
                "descricao": "Enviar imagens para uma tatuagem.",
            },
            {
                "id": 17,
                "codigo": "imagens:remover",
                "descricao": "Remover imagens de uma tatuagem.",
            },
            {
                "id": 18,
                "codigo": "imagens:aprovar",
                "descricao": "Aprovar ou recusar o desenho de uma tatuagem própria.",
            },
            {
                "id": 19,
                "codigo": "agendamentos:gerenciar",
                "descricao": "Agendar e cancelar sessões e retoques.",
            },
            {
                "id": 20,
                "codigo": "agendamentos:consultar",
                "descricao": "Consultar os agendamentos de uma tatuagem.",
            },
        ],
    )

    grupos_permissoes = sa.table(
        "grupos_permissoes",
        sa.column("grupo_id", sa.Integer()),
        sa.column("permissao_id", sa.Integer()),
    )
    op.bulk_insert(
        grupos_permissoes,
        [
            # Cliente envia referências, aprova o desenho e vê os horários.
            *(
                {"grupo_id": 1, "permissao_id": permissao_id}
                for permissao_id in [16, 18, 20]
            ),
            # Tatuador envia e remove imagens e administra a própria agenda.
            *(
                {"grupo_id": 2, "permissao_id": permissao_id}
                for permissao_id in [16, 17, 19, 20]
            ),
            # Administrador recebe as permissões novas; as antigas já existem.
            *(
                {"grupo_id": 3, "permissao_id": permissao_id}
                for permissao_id in [16, 17, 18, 19, 20]
            ),
        ],
    )

    op.execute(
        "SELECT setval(pg_get_serial_sequence('permissoes', 'id'), "
        "COALESCE((SELECT MAX(id) FROM permissoes), 1), true)"
    )


def downgrade() -> None:
    """Remove as permissões novas e depois as tabelas que as usam."""
    codigos = (
        "'imagens:enviar', 'imagens:remover', 'imagens:aprovar', "
        "'agendamentos:gerenciar', 'agendamentos:consultar'"
    )
    op.execute(
        "DELETE FROM grupos_permissoes WHERE permissao_id IN ("
        f"SELECT id FROM permissoes WHERE codigo IN ({codigos})"
        ")"
    )
    op.execute(f"DELETE FROM permissoes WHERE codigo IN ({codigos})")

    op.drop_index("uq_agendamentos_tatuador_horario", table_name="agendamentos")
    op.drop_table("agendamentos")
    op.drop_table("tatuagem_imagens")
