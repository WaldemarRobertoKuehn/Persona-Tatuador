"""Testes da atribuição de tatuador, sem banco de dados.

O serviço é testado com os repositórios trocados por funções simples. O que
importa aqui é a decisão: o pedido nasce com o tatuador padrão e a troca recusa
uma conta que não é do grupo tatuador.
"""

from datetime import date, time

import pytest

import repositorios.tatuagem as repositorio_tatuagens
import repositorios.usuario as repositorio_usuarios
import servicos.tatuagem as servico
from servicos.excecoes import AgendamentoConflitante


def test_pedido_nasce_com_o_tatuador_padrao(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_padrao_id",
        lambda: 7,
    )
    gravado = {}

    def criar(dados):
        gravado.update(dados)
        return {"id": 1, **dados}

    monkeypatch.setattr(repositorio_tatuagens, "criar_tatuagem", criar)

    servico.pedir_tatuagem(
        {
            "cliente_id": 3,
            "ideia": "Uma flor no antebraço",
            "local_do_corpo": "antebraço",
            "tamanho": 10.0,
        }
    )

    assert gravado["etapa"] == "pedida"
    assert gravado["tatuador_id"] == 7


def test_pedido_sem_tatuador_cadastrado_fica_sem_responsavel(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_padrao_id",
        lambda: None,
    )
    monkeypatch.setattr(
        repositorio_tatuagens,
        "criar_tatuagem",
        lambda dados: {"id": 1, **dados},
    )

    tatuagem = servico.pedir_tatuagem(
        {
            "cliente_id": 3,
            "ideia": "Uma flor no antebraço",
            "local_do_corpo": "antebraço",
            "tamanho": 10.0,
        }
    )

    assert tatuagem["tatuador_id"] is None


def test_atribuir_recusa_conta_que_nao_e_tatuador(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_por_id",
        lambda _: None,
    )

    with pytest.raises(ValueError):
        servico.atribuir_tatuador(1, 99)


def test_atribuir_grava_o_novo_responsavel(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_por_id",
        lambda usuario_id: {"id": usuario_id},
    )
    monkeypatch.setattr(
        repositorio_tatuagens,
        "atualizar_tatuador",
        lambda tatuagem_id, tatuador_id: (
            "ok",
            {"id": tatuagem_id, "tatuador_id": tatuador_id},
        ),
    )

    tatuagem = servico.atribuir_tatuador(1, 7)

    assert tatuagem["tatuador_id"] == 7


def test_atribuir_recusa_horario_ocupado_do_novo_tatuador(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_por_id",
        lambda usuario_id: {"id": usuario_id, "nome": "Vitor"},
    )
    monkeypatch.setattr(
        repositorio_tatuagens,
        "atualizar_tatuador",
        lambda tatuagem_id, tatuador_id: (
            "conflito",
            {"data": date(2026, 11, 9), "hora_inicio": time(10, 30)},
        ),
    )

    with pytest.raises(AgendamentoConflitante) as recusa:
        servico.atribuir_tatuador(1, 7)

    assert "Vitor" in str(recusa.value)
    assert "09/11/2026" in str(recusa.value)
    assert "10:30" in str(recusa.value)


def test_atribuir_tatuagem_inexistente_devolve_none(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_tatuador_por_id",
        lambda usuario_id: {"id": usuario_id, "nome": "Vitor"},
    )
    monkeypatch.setattr(
        repositorio_tatuagens,
        "atualizar_tatuador",
        lambda tatuagem_id, tatuador_id: ("nao_encontrada", None),
    )

    assert servico.atribuir_tatuador(999, 7) is None
