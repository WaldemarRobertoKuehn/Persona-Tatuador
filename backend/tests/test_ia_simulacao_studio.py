"""Testar as quatro personas sem chamar os provedores nem o banco."""

import sys
import types

import pytest

import ia.simulacao_studio as simulacao


def test_simular_atendimento_encadeia_as_quatro_personas(monkeypatch):
    chamadas = []
    respostas = iter(
        [
            "RESUMO: A cliente apresenta a ideia.\nFALA: Quero uma flor pequena.",
            "RESUMO: O atendimento identifica o que falta.\nFALA: Qual estilo você prefere?",
            "RESUMO: O tatuador pede alinhamento visual.\nFALA: Posso estudar algumas referências.",
            "RESUMO: A administração organiza o encaminhamento.\nFALA: Vamos alinhar os detalhes antes de agendar.",
        ]
    )

    modelos_falsos = types.ModuleType("ia.modelos")
    modelos_falsos.llm = object()
    monkeypatch.setitem(sys.modules, "ia.modelos", modelos_falsos)

    class AgenteFalso:
        def __init__(self, llm, *, role, goal):
            chamadas.append({"llm": llm, "role": role, "goal": goal})

        def run(self, prompt):
            chamadas[-1]["prompt"] = prompt
            return types.SimpleNamespace(text=next(respostas))

    monkeypatch.setattr(simulacao, "Agent", AgenteFalso)

    etapas = simulacao.simular_atendimento(
        "Cliente deseja uma flor pequena no antebraço."
    )

    assert [etapa["persona"] for etapa in etapas] == [
        "Cliente",
        "Atendente",
        "Tatuador(a)",
        "Administrador(a)",
    ]
    assert [etapa["etapa"] for etapa in etapas] == [1, 2, 3, 4]
    assert all(etapa["resumo"] and etapa["fala"] for etapa in etapas)
    assert "Cliente deseja uma flor pequena" in chamadas[0]["prompt"]
    assert "Cliente: Quero uma flor pequena." in chamadas[1]["prompt"]
    assert "Atendente: Qual estilo você prefere?" in chamadas[2]["prompt"]
    assert "Tatuador(a): Posso estudar algumas referências." in chamadas[3]["prompt"]


def test_resposta_sem_resumo_e_fala_e_recusada():
    with pytest.raises(simulacao.RespostaDePersonaInvalida):
        simulacao._separar_resumo_e_fala("Só uma resposta sem as partes esperadas.")
