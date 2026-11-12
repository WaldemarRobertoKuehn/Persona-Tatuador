"""Testar a rota e o controle de acesso da simulação fictícia."""

import pytest
from fastapi import HTTPException
from jangada_ai.errors import ProviderError

import rotas.simulacao_studio as rota_simulacao


def test_rota_devolve_quatro_etapas(monkeypatch):
    etapas = [
        {
            "etapa": indice,
            "persona": persona,
            "titulo": f"Etapa {indice}",
            "resumo": "Resumo fictício.",
            "fala": "Fala fictícia.",
        }
        for indice, persona in enumerate(
            ["Cliente", "Atendente", "Tatuador(a)", "Administrador(a)"],
            start=1,
        )
    ]
    chamadas = []
    monkeypatch.setattr(
        rota_simulacao,
        "simular_atendimento",
        lambda situacao: chamadas.append(situacao) or etapas,
    )

    resposta = rota_simulacao.criar_simulacao_studio(
        rota_simulacao.SimulacaoStudioEntrada(
            situacao="Uma cliente quer uma tatuagem floral pequena."
        )
    )

    assert resposta == {"etapas": etapas}
    assert chamadas == ["Uma cliente quer uma tatuagem floral pequena."]


def test_rota_responde_503_quando_provedores_falham(monkeypatch):
    def falhar(_):
        raise ProviderError("falha fictícia")

    monkeypatch.setattr(rota_simulacao, "simular_atendimento", falhar)

    with pytest.raises(HTTPException) as erro:
        rota_simulacao.criar_simulacao_studio(
            rota_simulacao.SimulacaoStudioEntrada(
                situacao="Uma cliente quer uma tatuagem floral pequena."
            )
        )

    assert erro.value.status_code == 503
    assert "Tente novamente" in erro.value.detail


def test_rota_restringe_simulacao_a_administrador():
    rota = rota_simulacao.roteador_simulacao_studio.routes[0]
    verificar_permissao = rota.dependencies[0].dependency

    assert verificar_permissao(
        usuario={"permissoes": ["grupos:consultar"]}
    ) == {"permissoes": ["grupos:consultar"]}
    with pytest.raises(HTTPException) as erro:
        verificar_permissao(usuario={"permissoes": ["passos:listar_todos"]})

    assert erro.value.status_code == 403
