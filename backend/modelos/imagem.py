"""Modelo SQLAlchemy das imagens de uma tatuagem.

A imagem é guardada no próprio PostgreSQL, na coluna conteudo, para o projeto não
depender de um serviço externo de arquivos. O conteúdo fica separado dos metadados:
as listagens leem só nome, tipo e status, e o arquivo só é carregado quando a tela
vai mostrar a imagem.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String, func

from banco import Base

# Estes imports registram as tabelas apontadas pelas ForeignKeys no desenho do
# SQLAlchemy. Sem eles, o Alembic não teria tatuagens e usuarios no metadata.
from modelos.tatuagem import Tatuagem
from modelos.usuario import Usuario


class TatuagemImagem(Base):
    """A tabela tatuagem_imagens: o desenho ou a referência de uma tatuagem."""

    __tablename__ = "tatuagem_imagens"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # O CASCADE garante que as imagens somem junto com a tatuagem, como já
    # acontece com os passos.
    tatuagem_id = Column(
        Integer,
        ForeignKey(
            "tatuagens.id",
            name="fk_tatuagem_imagens_tatuagem",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    nome = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    tamanho_bytes = Column(Integer, nullable=False)

    # tipo separa a referência enviada pelo cliente do desenho que o tatuador
    # produz e o cliente aprova. A lista aceita é decidida no serviço.
    tipo = Column(
        String(20),
        nullable=False,
        default="desenho",
        server_default="desenho",
    )

    # status é pendente, aprovada ou recusada. Só o desenho pode ser aprovado.
    status = Column(
        String(20),
        nullable=False,
        default="pendente",
        server_default="pendente",
    )

    # O arquivo em si. LargeBinary vira BYTEA no PostgreSQL.
    conteudo = Column(LargeBinary, nullable=False)

    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    aprovada_em = Column(DateTime(timezone=True), nullable=True)
    recusada_em = Column(DateTime(timezone=True), nullable=True)
    motivo_recusa = Column(String(500), nullable=True)

    # Guarda quem aprovou, para a auditoria da etapa que a aprovação mudou.
    aprovada_por_usuario_id = Column(
        Integer,
        ForeignKey(
            "usuarios.id",
            name="fk_tatuagem_imagens_aprovador",
        ),
        nullable=True,
    )
