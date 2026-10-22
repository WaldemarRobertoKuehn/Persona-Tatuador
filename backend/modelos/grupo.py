"""NOVO: modelos de grupos, permissões e vínculo entre ambos."""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from banco import Base


# NOVO: tabela associativa para permitir várias permissões por grupo e reutilizar
# uma permissão em grupos diferentes.
grupos_permissoes = Table(
    "grupos_permissoes",
    Base.metadata,
    Column(
        "grupo_id",
        Integer,
        ForeignKey("grupos.id", name="fk_grupos_permissoes_grupo"),
        primary_key=True,
    ),
    Column(
        "permissao_id",
        Integer,
        ForeignKey("permissoes.id", name="fk_grupos_permissoes_permissao"),
        primary_key=True,
    ),
)


class Grupo(Base):
    """NOVO: grupo persistente ao qual cada conta pertence."""

    __tablename__ = "grupos"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_grupos_codigo"),
        UniqueConstraint("nome", name="uq_grupos_nome"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), nullable=False)
    nome = Column(String(80), nullable=False)


class Permissao(Base):
    """NOVO: permissão nomeada de uma operação ou escopo de rota."""

    __tablename__ = "permissoes"
    __table_args__ = (UniqueConstraint("codigo", name="uq_permissoes_codigo"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(100), nullable=False)
    descricao = Column(String(250), nullable=False)
