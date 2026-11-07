"""Testes da regra de agenda, sem banco de dados.

Os repositórios são trocados por funções simples com monkeypatch. O que está
sendo testado aqui é o expediente, o cálculo da hora de fim, o bloqueio por
tatuador e a etapa mínima para agendar.
"""

from datetime import date, datetime, time

import pytest

import servicos.agendamento as servico
from servicos.excecoes import (
    AgendamentoDeOutroTatuador,
    AgendamentoJaCancelado,
    AgendamentoNoPassado,
    DataForaDoExpediente,
    EtapaNaoPermiteAgendamento,
    HorarioForaDoExpediente,
    HorarioIndisponivel,
    TipoDeAgendamentoDesconhecido,
)

# Uma sexta-feira às 12h, no fuso do estúdio. Os testes usam datas de novembro
# de 2026: dia 7 é sábado, dia 8 é domingo e dia 9 é segunda.
AGORA = datetime(2026, 11, 6, 12, 0, tzinfo=servico.FUSO_ESTUDIO)
TATUAGEM = {"id": 1, "tatuador_id": 2, "etapa": "desenho aprovado"}
TATUADOR = {"id": 2, "papel": "tatuador"}


@pytest.fixture(autouse=True)
def agora_fixa(monkeypatch):
    """Mantém a regra de horário passado previsível em todos os testes."""
    monkeypatch.setattr(servico, "_agora", lambda: AGORA)


def test_segunda_tem_oito_horarios(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [],
    )

    disponibilidade = servico.obter_disponibilidade(TATUAGEM, date(2026, 11, 9))

    assert disponibilidade["aberto"] is True
    assert [horario["hora_inicio"] for horario in disponibilidade["horarios"]] == [
        time(8, 30),
        time(9, 30),
        time(10, 30),
        time(13, 30),
        time(14, 30),
        time(15, 30),
        time(16, 30),
        time(17, 30),
    ]


def test_sabado_tem_quatro_horarios(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [],
    )

    disponibilidade = servico.obter_disponibilidade(TATUAGEM, date(2026, 11, 7))

    assert [horario["hora_inicio"] for horario in disponibilidade["horarios"]] == [
        time(8, 0),
        time(9, 0),
        time(10, 0),
        time(11, 0),
    ]


def test_domingo_fica_fechado(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: pytest.fail("domingo não deveria consultar agendamentos"),
    )

    disponibilidade = servico.obter_disponibilidade(TATUAGEM, date(2026, 11, 8))

    assert disponibilidade == {"data": date(2026, 11, 8), "aberto": False, "horarios": []}


def test_horario_ocupado_fica_indisponivel(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [
            {"id": 9, "hora_inicio": time(8, 30), "hora_fim": time(9, 30)}
        ],
    )

    disponibilidade = servico.obter_disponibilidade(TATUAGEM, date(2026, 11, 9))
    primeiro = disponibilidade["horarios"][0]

    assert primeiro["disponivel"] is False
    assert primeiro["agendamento_id"] == 9


def test_horario_que_ja_passou_fica_indisponivel(monkeypatch):
    monkeypatch.setattr(servico, "_agora", lambda: datetime(2026, 11, 9, 9, 0, tzinfo=servico.FUSO_ESTUDIO))
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [],
    )

    disponibilidade = servico.obter_disponibilidade(TATUAGEM, date(2026, 11, 9))
    por_horario = {
        horario["hora_inicio"]: horario["disponivel"]
        for horario in disponibilidade["horarios"]
    }

    assert por_horario[time(8, 30)] is False
    assert por_horario[time(9, 30)] is True


def test_agendar_calcula_hora_de_fim(monkeypatch):
    gravado = {}
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [],
    )

    def criar(tatuagem_id, dados):
        gravado.update(dados)
        return {"id": 10, **dados}

    monkeypatch.setattr(servico.repositorio_agendamentos, "criar_agendamento", criar)

    agendamento = servico.agendar(
        1,
        TATUAGEM,
        TATUADOR,
        {
            "tipo": "sessão",
            "data": date(2026, 11, 9),
            "hora_inicio": time(8, 30),
        },
    )

    assert agendamento["id"] == 10
    assert gravado["hora_fim"] == time(9, 30)
    assert gravado["tatuador_id"] == TATUAGEM["tatuador_id"]


def test_agendar_recusa_horario_ocupado(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "listar_ativos_do_tatuador",
        lambda *_: [
            {"id": 9, "hora_inicio": time(8, 30), "hora_fim": time(9, 30)}
        ],
    )

    with pytest.raises(HorarioIndisponivel):
        servico.agendar(
            1,
            TATUAGEM,
            TATUADOR,
            {
                "tipo": "sessão",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 30),
            },
        )


def test_agendar_recusa_tatuagem_ainda_pedida(monkeypatch):
    with pytest.raises(EtapaNaoPermiteAgendamento):
        servico.agendar(
            1,
            {**TATUAGEM, "etapa": "pedida"},
            TATUADOR,
            {
                "tipo": "sessão",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 30),
            },
        )


def test_agendar_recusa_agenda_de_outro_tatuador(monkeypatch):
    with pytest.raises(AgendamentoDeOutroTatuador):
        servico.agendar(
            1,
            TATUAGEM,
            {"id": 3, "papel": "tatuador"},
            {
                "tipo": "sessão",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 30),
            },
        )


def test_agendar_recusa_dia_fechado(monkeypatch):
    with pytest.raises(DataForaDoExpediente):
        servico.agendar(
            1,
            TATUAGEM,
            TATUADOR,
            {
                "tipo": "sessão",
                "data": date(2026, 11, 8),
                "hora_inicio": time(8, 0),
            },
        )


def test_agendar_recusa_horario_fora_da_tabela(monkeypatch):
    with pytest.raises(HorarioForaDoExpediente):
        servico.agendar(
            1,
            TATUAGEM,
            TATUADOR,
            {
                "tipo": "sessão",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 0),
            },
        )


def test_agendar_recusa_horario_passado(monkeypatch):
    monkeypatch.setattr(servico, "_agora", lambda: datetime(2026, 11, 9, 9, 0, tzinfo=servico.FUSO_ESTUDIO))

    with pytest.raises(AgendamentoNoPassado):
        servico.agendar(
            1,
            TATUAGEM,
            TATUADOR,
            {
                "tipo": "sessão",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 30),
            },
        )


def test_agendar_recusa_tipo_desconhecido(monkeypatch):
    with pytest.raises(TipoDeAgendamentoDesconhecido):
        servico.agendar(
            1,
            TATUAGEM,
            TATUADOR,
            {
                "tipo": "cobertura",
                "data": date(2026, 11, 9),
                "hora_inicio": time(8, 30),
            },
        )


def test_cancelar_agendamento_ja_cancelado(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_agendamentos,
        "buscar_agendamento",
        lambda *_: {"id": 4, "tatuador_id": 2, "status": "cancelado"},
    )

    with pytest.raises(AgendamentoJaCancelado):
        servico.cancelar_agendamento(1, 4, TATUAGEM, TATUADOR)
