"""Testes da regra de imagens, sem banco de dados.

O repositório é substituído por funções com monkeypatch. Os testes cobrem o
tipo forçado do cliente, o limite do arquivo e a aprovação que registra o passo
"desenho aprovado".
"""

import pytest

import servicos.imagem as servico
from servicos.excecoes import (
    AprovacaoDoClienteNecessaria,
    ArquivoDeImagemInvalido,
    ImagemJaAprovada,
    ImagemNaoAprovavel,
    TipoDeImagemDesconhecido,
)

TATUAGEM = {"id": 1, "etapa": "pedida"}
CLIENTE = {"id": 7, "papel": "cliente"}
TATUADOR = {"id": 2, "papel": "tatuador"}


def test_cliente_envia_sempre_como_referencia(monkeypatch):
    def criar(tatuagem_id, dados):
        return {"tatuagem_id": tatuagem_id, **dados}

    monkeypatch.setattr(servico.repositorio_imagens, "criar_imagem", criar)

    imagem = servico.enviar_imagem(
        1,
        TATUAGEM,
        CLIENTE,
        "foto.png",
        "desenho",
        "image/png",
        b"conteudo",
    )

    assert imagem["tipo"] == "referencia"
    assert imagem["nome"] == "foto.png"


def test_tatuador_envia_desenho(monkeypatch):
    def criar(tatuagem_id, dados):
        return {"tatuagem_id": tatuagem_id, **dados}

    monkeypatch.setattr(servico.repositorio_imagens, "criar_imagem", criar)

    imagem = servico.enviar_imagem(
        1,
        TATUAGEM,
        TATUADOR,
        "leao.png",
        "desenho",
        "image/png",
        b"conteudo",
    )

    assert imagem["tipo"] == "desenho"


def test_arquivo_precisa_ser_imagem_aceita(monkeypatch):
    with pytest.raises(ArquivoDeImagemInvalido):
        servico.enviar_imagem(
            1,
            TATUAGEM,
            TATUADOR,
            "arquivo.pdf",
            "desenho",
            "application/pdf",
            b"conteudo",
        )


def test_arquivo_acima_do_limite_e_recusado(monkeypatch):
    with pytest.raises(ArquivoDeImagemInvalido):
        servico.enviar_imagem(
            1,
            TATUAGEM,
            TATUADOR,
            "grande.png",
            "desenho",
            "image/png",
            b"x" * (servico.TAMANHO_MAXIMO_IMAGEM + 1),
        )


def test_tipo_de_imagem_desconhecido(monkeypatch):
    with pytest.raises(TipoDeImagemDesconhecido):
        servico.enviar_imagem(
            1,
            TATUAGEM,
            TATUADOR,
            "foto.png",
            "paisagem",
            "image/png",
            b"conteudo",
        )


def test_cliente_aprova_desenho_e_registra_passo(monkeypatch):
    imagem = {
        "id": 5,
        "tipo": "desenho",
        "status": "pendente",
        "nome": "leao.png",
    }
    chamadas = {}

    monkeypatch.setattr(
        servico.repositorio_imagens,
        "buscar_imagem",
        lambda *_: imagem,
    )
    monkeypatch.setattr(
        servico.servico_passos,
        "aplicar_passo",
        lambda *_: "desenho aprovado",
    )

    def registrar(tatuagem_id, dados, tatuagem=None, aprovado_pelo_cliente=False):
        chamadas.update(
            tatuagem_id=tatuagem_id,
            dados=dados,
            aprovado_pelo_cliente=aprovado_pelo_cliente,
        )
        return {"id": 1, "tipo": "desenho aprovado"}

    monkeypatch.setattr(servico.servico_passos, "registrar_passo", registrar)
    monkeypatch.setattr(
        servico.repositorio_imagens,
        "aprovar_imagem",
        lambda *_: {**imagem, "status": "aprovada"},
    )

    aprovada = servico.aprovar_imagem(1, 5, TATUAGEM, CLIENTE)

    assert aprovada["status"] == "aprovada"
    assert chamadas["tatuagem_id"] == 1
    assert chamadas["aprovado_pelo_cliente"] is True
    assert chamadas["dados"]["tipo"] == "desenho aprovado"


def test_aprovacao_ja_feita_nao_duplica_passo(monkeypatch):
    imagem = {
        "id": 5,
        "tipo": "desenho",
        "status": "aprovada",
        "nome": "leao.png",
    }
    monkeypatch.setattr(
        servico.repositorio_imagens,
        "buscar_imagem",
        lambda *_: imagem,
    )
    monkeypatch.setattr(
        servico.servico_passos,
        "registrar_passo",
        lambda *args, **kwargs: pytest.fail("não deveria registrar outro passo"),
    )

    aprovada = servico.aprovar_imagem(1, 5, TATUAGEM, CLIENTE)

    assert aprovada is imagem


def test_tatuador_nao_aprova_desenho(monkeypatch):
    with pytest.raises(AprovacaoDoClienteNecessaria):
        servico.aprovar_imagem(1, 5, TATUAGEM, TATUADOR)


def test_referencia_nao_pode_ser_aprovada(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_imagens,
        "buscar_imagem",
        lambda *_: {"id": 5, "tipo": "referencia", "status": "pendente"},
    )

    with pytest.raises(ImagemNaoAprovavel):
        servico.aprovar_imagem(1, 5, TATUAGEM, CLIENTE)


def test_desenho_aprovado_nao_pode_ser_recusado(monkeypatch):
    monkeypatch.setattr(
        servico.repositorio_imagens,
        "buscar_imagem",
        lambda *_: {"id": 5, "tipo": "desenho", "status": "aprovada"},
    )

    with pytest.raises(ImagemJaAprovada):
        servico.recusar_imagem(1, 5, "mudei de ideia", CLIENTE)
