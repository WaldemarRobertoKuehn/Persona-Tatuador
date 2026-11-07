import hashlib

import pytest
from pydantic import ValidationError

import repositorios.usuario as repositorio_usuarios
import seguranca
import servicos.usuario as servico_usuarios
from esquemas.usuario import RedefinirSenhaEntrada


def test_solicitacao_grava_hash_e_envia_link(monkeypatch):
    conta = {"id": 7, "nome": "Ana", "email": "ana@example.com"}
    gravacao = {}
    emails = []

    monkeypatch.setattr(repositorio_usuarios, "buscar_por_email", lambda _: conta)

    def guardar_token(usuario_id, token_hash, expira_em, solicitado_em, limite):
        gravacao.update(
            usuario_id=usuario_id,
            token_hash=token_hash,
            expira_em=expira_em,
            solicitado_em=solicitado_em,
            limite=limite,
        )
        return True

    monkeypatch.setattr(repositorio_usuarios, "guardar_token_redefinicao", guardar_token)
    monkeypatch.setattr(
        servico_usuarios.configuracao,
        "endereco_do_front",
        lambda: "https://tracofino.example",
    )
    monkeypatch.setattr(
        servico_usuarios.servico_email,
        "enviar_link_redefinicao",
        lambda destino, nome, link: emails.append((destino, nome, link)),
    )

    servico_usuarios.solicitar_redefinicao_senha("ana@example.com")

    token = emails[0][2].split("redefinir-senha=", maxsplit=1)[1]
    assert emails[0][:2] == (conta["email"], conta["nome"])
    assert gravacao["usuario_id"] == conta["id"]
    assert gravacao["token_hash"] == hashlib.sha256(token.encode()).hexdigest()
    assert gravacao["token_hash"] != token
    assert (gravacao["expira_em"] - gravacao["solicitado_em"]).total_seconds() == 900


def test_email_desconhecido_nao_envia_mensagem(monkeypatch):
    emails = []
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_email", lambda _: None)
    monkeypatch.setattr(
        servico_usuarios.servico_email,
        "enviar_link_redefinicao",
        lambda *args: emails.append(args),
    )

    servico_usuarios.solicitar_redefinicao_senha("inexistente@example.com")

    assert emails == []


def test_redefinicao_salva_hash_e_entrega_hash_do_token(monkeypatch):
    valores = {}
    token_hash = hashlib.sha256(b"token-secreto").hexdigest()
    monkeypatch.setattr(seguranca, "gerar_hash", lambda senha: f"hash:{senha}")

    def redefinir(hash_token, hash_senha, agora):
        valores.update(token=hash_token, senha=hash_senha, agora=agora)
        return True

    monkeypatch.setattr(
        repositorio_usuarios,
        "redefinir_senha_com_token",
        redefinir,
    )

    assert servico_usuarios.redefinir_senha("token-secreto", "senha-nova")
    assert valores["token"] == token_hash
    assert valores["senha"] == "hash:senha-nova"


def test_esquema_recusa_senhas_de_confirmacao_diferentes():
    with pytest.raises(ValidationError, match="As senhas não coincidem"):
        RedefinirSenhaEntrada(
            token="t" * 32,
            senha="senha-nova",
            confirmacao_senha="senha-diferente",
        )