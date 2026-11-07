"""Modelo SQLAlchemy dos agendamentos de sessão e retoque.

Cada agendamento ocupa um horário de uma hora na agenda de um tatuador. O índice
único parcial impede dois agendamentos ativos no mesmo horário do mesmo tatuador,
mas permite que um horário cancelado volte a ser usado.
"""

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    func,
    text,
)

from banco import Base

# Estes imports registram as tabelas apontadas pelas ForeignKeys no metadata.
from modelos.tatuagem import Tatuagem
from modelos.usuario import Usuario


class Agendamento(Base):
    """A tabela agendamentos: uma sessão ou o retoque final marcado."""

    __tablename__ = "agendamentos"
    __table_args__ = (
        # O WHERE parcial é o que libera o horário quando o agendamento é
        # cancelado, sem apagar o registro do histórico.
        Index(
            "uq_agendamentos_tatuador_horario",
            "tatuador_id",
            "data",
            "hora_inicio",
            unique=True,
            postgresql_where=text("status = 'agendado'"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)

    tatuagem_id = Column(
        Integer,
        ForeignKey(
            "tatuagens.id",
            name="fk_agendamentos_tatuagem",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # O tatuador é o dono da agenda. O bloqueio de horário é por tatuador.
    tatuador_id = Column(
        Integer,
        ForeignKey("usuarios.id", name="fk_agendamentos_tatuador"),
        nullable=False,
    )

    # tipo é "sessão" ou "retoque". A lista é validada no serviço.
    tipo = Column(String(20), nullable=False)

    data = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="agendado",
        server_default="agendado",
    )

    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
