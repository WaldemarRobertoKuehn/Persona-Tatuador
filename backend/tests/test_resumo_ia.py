"""Testar a rota de rascunho sem banco nem chamadas a provedores."""

import pytest
from fastapi import HTTPException
from fastapi.params import Depends as DependenciaFastAPI
from jangada_ai.errors import ProviderError

# Importar a rota para substituir a função de IA por resultados fictícios.
import rotas.resumo_ia as rota_resumo_ia
import rotas.dependencias as dependencias


# Confirmar que a rota devolve o rascunho sem acionar operações de gravação.
def test_rota_devolve_rascunho_sem_persistir(monkeypatch):
    chamadas = []
    tatuagem_ficticia = {
        "id": 23,
        "etapa": "em sessões",
        "cliente_id": 987,
        "nome_da_cliente": "Pessoa Fictícia",
    }

    # Substituir a função da camada de IA por uma resposta fictícia.
    monkeypatch.setattr(
        rota_resumo_ia,
        "resumir_historico",
        lambda tatuagem: chamadas.append(tatuagem) or "Rascunho fictício.",
    )

    # Chamar a função da rota com a tatuagem já validada pela dependência.
    resposta = rota_resumo_ia.gerar_resumo_ia(23, tatuagem_ficticia)

    # Conferir resposta, passagem do registro e ausência de persistência.
    assert resposta == {"rascunho": "Rascunho fictício."}
    assert chamadas == [tatuagem_ficticia]


# Converter apenas falhas normalizadas do Jangada em HTTP 503 para o frontend.
def test_rota_responde_503_quando_jangada_falha(monkeypatch):
    # Simular que o Jangada não conseguiu obter resposta dos provedores.
    def falhar(_):
        raise ProviderError("falha fictícia")

    monkeypatch.setattr(rota_resumo_ia, "resumir_historico", falhar)

    # Conferir o status e a frase estável, sem detalhes internos do provedor.
    with pytest.raises(HTTPException) as erro:
        rota_resumo_ia.gerar_resumo_ia(
            23,
            {"id": 23, "etapa": "pedida"},
        )

    assert erro.value.status_code == 503
    assert erro.value.detail == (
        "A IA não conseguiu gerar o resumo agora. Tente novamente mais tarde."
    )


# Garantir que a rota depende do mesmo escopo de acesso ao histórico oficial.
def test_rota_exige_permissao_e_titularidade(monkeypatch):
    dependencia = rota_resumo_ia.gerar_resumo_ia.__defaults__[0]
    tatuagem_ficticia = {"id": 23, "cliente_id": 987, "etapa": "pedida"}

    # Substituir a consulta ao banco e vincular o acesso próprio à cliente fictícia.
    monkeypatch.setattr(
        dependencias.servico_tatuagens,
        "buscar_tatuagem",
        lambda tatuagem_id: tatuagem_ficticia if tatuagem_id == 23 else None,
    )

    # Usar a permissão de leitura já atribuída ao cliente e conferir a titularidade.
    assert isinstance(dependencia, DependenciaFastAPI)
    assert dependencia.dependency(
        tatuagem_id=23,
        usuario={
            "cliente_id": 987,
            "permissoes": ["passos:listar_proprios"],
        },
    ) == tatuagem_ficticia

    # Recusar um grupo sem permissão antes de expor a tatuagem consultada.
    with pytest.raises(HTTPException) as erro:
        dependencia.dependency(
            tatuagem_id=23,
            usuario={"cliente_id": 987, "permissoes": []},
        )

    assert erro.value.status_code == 403
    assert "/tatuagens/{tatuagem_id}/resumo-ia" in {
        rota.path for rota in rota_resumo_ia.roteador_resumo_ia.routes
    }
