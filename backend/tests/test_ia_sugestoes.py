"""Testar a chamada de resumo com um Agent falso e histórico fictício."""

import sys
import types
from datetime import date

import pytest

# Importar o serviço para substituir a leitura do banco por dados fictícios.
import servicos.passo as servico_passos

# Importar a instrução e a função que monta a chamada ao Agent.
import ia.sugestoes as sugestoes


# Confirmar que o Agent recebe a tool vinculada e devolve apenas seu texto.
def test_resumir_historico_chama_agent_com_dados_ficticios(monkeypatch):
    chamadas_de_leitura = []
    chamadas_de_gravacao = []
    passos_ficticios = [
        {
            "id": 31,
            "tatuagem_id": 23,
            "tipo": "sessão",
            "data": date(2026, 5, 10),
            "observacao": "Contorno realizado.",
        }
    ]

    # Substituir a consulta ao banco e detectar qualquer chamada de gravação.
    monkeypatch.setattr(
        servico_passos,
        "listar_passos",
        lambda tatuagem_id: chamadas_de_leitura.append(tatuagem_id)
        or passos_ficticios,
    )
    monkeypatch.setattr(
        servico_passos,
        "registrar_passo",
        lambda *args, **kwargs: chamadas_de_gravacao.append((args, kwargs)),
    )

    # Fornecer um modelo falso para não carregar configuração nem chamar provedores.
    modelos_falsos = types.ModuleType("ia.modelos")
    modelos_falsos.llm = object()
    monkeypatch.setitem(sys.modules, "ia.modelos", modelos_falsos)

    agentes_criados = []

    # Simular o Agent chamando a tool como faria durante a execução.
    class AgenteFalso:
        def __init__(self, llm, *, role, goal, tools, on_tool_result):
            agentes_criados.append(
                {
                    "llm": llm,
                    "role": role,
                    "goal": goal,
                    "tools": tools,
                    "on_tool_result": on_tool_result,
                }
            )

        def run(self, tarefa):
            assert "Consultar o histórico" in tarefa
            historico = self.configuracao["tools"][0]()
            assert '"numero": 1' in historico
            self.configuracao["on_tool_result"](
                None,
                types.SimpleNamespace(is_error=False),
            )
            return types.SimpleNamespace(
                text="O contorno foi realizado em 10/05/2026.\nReferências: [1]"
            )

    # Manter a configuração do agente disponível para o método run do falso.
    def criar_agente(llm, *, role, goal, tools, on_tool_result):
        agente = AgenteFalso(
            llm,
            role=role,
            goal=goal,
            tools=tools,
            on_tool_result=on_tool_result,
        )
        agente.configuracao = agentes_criados[-1]
        return agente

    # Substituir a classe externa pelo agente falso sem fazer chamadas de rede.
    monkeypatch.setattr(sugestoes, "Agent", criar_agente)

    # Solicitar o resumo usando apenas campos da tatuagem necessários à tool.
    rascunho = sugestoes.resumir_historico(
        {
            "id": 23,
            "etapa": "em sessões",
            "cliente_id": 987,
            "nome_da_cliente": "Pessoa Fictícia",
        }
    )

    # Conferir instrução, vínculo da leitura e ausência de qualquer gravação.
    assert rascunho.endswith("Referências: [1]")
    assert agentes_criados[0]["goal"] == sugestoes.INSTRUCAO
    assert agentes_criados[0]["role"] == "Resumidor do histórico de uma tatuagem"
    assert (
        agentes_criados[0]["on_tool_result"]
        is sugestoes._interromper_se_ferramenta_falhar
    )
    assert chamadas_de_leitura == [23]
    assert chamadas_de_gravacao == []
    assert "Pessoa Fictícia" not in sugestoes.INSTRUCAO
    assert "987" not in sugestoes.INSTRUCAO


# Fazer a falha da consulta interromper o Agent em vez de virar uma resposta final.
def test_falha_na_ferramenta_nao_vira_resposta_de_sucesso():
    # Passar um resultado de erro para a função de controle e exigir a exceção.
    with pytest.raises(RuntimeError, match="Não foi possível consultar"):
        sugestoes._interromper_se_ferramenta_falhar(
            None,
            types.SimpleNamespace(is_error=True),
        )
