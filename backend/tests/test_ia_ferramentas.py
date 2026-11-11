"""Testar a tool de leitura do histórico com dados fictícios e sem banco."""

import json
from datetime import date

import pytest

# Importar o serviço para substituir a leitura pelo histórico fictício do teste.
import servicos.passo as servico_passos

# Importar a fábrica e o registro de tools que a funcionalidade usará.
from ia.ferramentas import FERRAMENTAS, criar_ferramenta_historico


# Confirmar que a tool consulta somente o histórico vinculado e não grava passos.
def test_ferramenta_le_historico_sem_gravar(monkeypatch):
    chamadas_de_leitura = []
    chamadas_de_gravacao = []
    passos_ficticios = [
        {
            "id": 31,
            "tatuagem_id": 23,
            "tipo": "desenho aprovado",
            "data": date(2026, 5, 2),
            "observacao": "Desenho confirmado pela cliente.",
        },
        {
            "id": 32,
            "tatuagem_id": 23,
            "tipo": "sessão",
            "data": date(2026, 5, 10),
            "observacao": "Contorno realizado.",
        },
    ]

    # Substituir a consulta ao banco e fazer qualquer tentativa de gravação falhar.
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

    # Passar dados fictícios com campos pessoais para garantir que não saiam no
    # resultado entregue à IA.
    ferramenta = criar_ferramenta_historico(
        {
            "id": 23,
            "etapa": "em sessões",
            "cliente_id": 987,
            "nome_da_cliente": "Pessoa Fictícia",
        }
    )
    resultado = json.loads(ferramenta())

    # Conferir conteúdo, numeração, vínculo fixo e ausência de dados pessoais.
    assert chamadas_de_leitura == [23]
    assert chamadas_de_gravacao == []
    assert resultado == {
        "etapa_atual": "em sessões",
        "passos": [
            {
                "numero": 1,
                "tipo": "desenho aprovado",
                "data": "2026-05-02",
                "observacao": "Desenho confirmado pela cliente.",
            },
            {
                "numero": 2,
                "tipo": "sessão",
                "data": "2026-05-10",
                "observacao": "Contorno realizado.",
            },
        ],
    }
    assert "987" not in json.dumps(resultado)
    assert "Pessoa Fictícia" not in json.dumps(resultado)


# Impedir que a chamada da tool aceite um id escolhido pelo modelo.
def test_ferramenta_nao_aceita_id_como_argumento(monkeypatch):
    ids_consultados = []

    # Substituir a leitura para registrar qual tatuagem foi consultada.
    monkeypatch.setattr(
        servico_passos,
        "listar_passos",
        lambda tatuagem_id: ids_consultados.append(tatuagem_id) or [],
    )

    # Vincular a tool a um registro fictício e rejeitar qualquer argumento externo.
    ferramenta = criar_ferramenta_historico({"id": 23, "etapa": "pedida"})
    ferramenta()

    with pytest.raises(TypeError):
        ferramenta(999)

    assert ids_consultados == [23]
    assert FERRAMENTAS == [criar_ferramenta_historico]
