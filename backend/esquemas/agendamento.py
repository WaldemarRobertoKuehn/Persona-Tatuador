"""Esquemas Pydantic de agendamento e disponibilidade.

A hora de fim não vem do front: o serviço calcula uma hora depois do início. A
disponibilidade devolve todos os horários do dia, com o indicador de livre ou
ocupado, para a tela não repetir a regra de expediente.
"""

from datetime import date, datetime, time

from pydantic import BaseModel, Field


class AgendamentoEntrada(BaseModel):
    """O que o tatuador manda ao marcar uma sessão ou o retoque."""

    tipo: str = Field(
        min_length=3,
        max_length=20,
        description='O tipo do agendamento: "sessão" ou "retoque".',
    )
    data: date
    hora_inicio: time


class AgendamentoSaida(BaseModel):
    """Um agendamento já gravado, com o nome do tatuador responsável."""

    id: int
    tatuagem_id: int
    tatuador_id: int
    tatuador_nome: str
    tipo: str
    data: date
    hora_inicio: time
    hora_fim: time
    status: str
    criado_em: datetime


class HorarioDisponivel(BaseModel):
    """Um horário de uma hora na agenda do tatuador."""

    hora_inicio: time
    hora_fim: time
    disponivel: bool
    agendamento_id: int | None = None


class DisponibilidadeSaida(BaseModel):
    """Todos os horários de um dia, mesmo quando o estúdio está fechado."""

    data: date
    aberto: bool
    horarios: list[HorarioDisponivel]
