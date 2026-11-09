import pytest

import nome_usuario
import repositorios.usuario as repositorio_usuarios
import seguranca
import servicos.usuario as servico_usuarios
from esquemas.usuario import CredenciaisEntrada


def test_nome_vira_usuario_sem_acentos():
    assert nome_usuario.transformar_em_usuario("Fábio Boeing") == "fabio.boeing"


def test_nome_vazio_tem_usuario_padrao():
    assert nome_usuario.transformar_em_usuario("   ") == "usuario"


def test_nome_repetido_recebe_sufixo():
    usados = {"ana", "ana2"}

    assert (
        nome_usuario.gerar_usuario_unico("Ana", lambda candidato: candidato in usados)
        == "ana3"
    )


def test_login_por_email(monkeypatch):
    conta = {
        "id": 1,
        "email": "ana@exemplo-real.com",
        "usuario": "ana",
        "senha_hash": "hash",
    }
    consultas = []

    def buscar(identificador):
        consultas.append(identificador)
        return conta

    monkeypatch.setattr(repositorio_usuarios, "buscar_por_identificador", buscar)
    monkeypatch.setattr(seguranca, "verificar_senha", lambda senha, hash: True)

    assert servico_usuarios.autenticar("Ana@Exemplo-Real.com", "senha123") == conta
    assert consultas == ["ana@exemplo-real.com"]


def test_login_por_usuario(monkeypatch):
    conta = {
        "id": 1,
        "email": "ana@exemplo-real.com",
        "usuario": "ana",
        "senha_hash": "hash",
    }

    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_por_identificador",
        lambda identificador: conta if identificador == "ana" else None,
    )
    monkeypatch.setattr(seguranca, "verificar_senha", lambda senha, hash: True)

    assert servico_usuarios.autenticar("ANA", "senha123") == conta


def test_login_recusa_senha_errada(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_por_identificador",
        lambda identificador: {"id": 1, "senha_hash": "hash"},
    )
    monkeypatch.setattr(seguranca, "verificar_senha", lambda senha, hash: False)

    assert servico_usuarios.autenticar("ana", "errada") is None


def test_definir_usuario_recusa_um_que_ja_e_de_outra_conta(monkeypatch):
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_por_usuario",
        lambda usuario: {"id": 2, "usuario": usuario},
    )

    def nao_atualizar(*args, **kwargs):
        raise AssertionError("o usuário repetido não deveria ser gravado")

    monkeypatch.setattr(repositorio_usuarios, "atualizar_usuario", nao_atualizar)

    assert servico_usuarios.definir_usuario(1, "ana") is False


def test_definir_usuario_grava_quando_esta_livre(monkeypatch):
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_usuario", lambda _: None)
    gravado = {}

    def atualizar(usuario_id, usuario):
        gravado["id"] = usuario_id
        gravado["usuario"] = usuario

    monkeypatch.setattr(repositorio_usuarios, "atualizar_usuario", atualizar)

    assert servico_usuarios.definir_usuario(1, "  Ana.Silva  ") is True
    assert gravado == {"id": 1, "usuario": "ana.silva"}


def test_credenciais_aceitam_identificador_e_email():
    por_usuario = CredenciaisEntrada(identificador="ANA", senha="senha123")
    por_email = CredenciaisEntrada(email="ana@exemplo-real.com", senha="senha123")

    assert por_usuario.identificador == "ana"
    assert por_email.identificador == "ana@exemplo-real.com"


def test_credenciais_recusam_identificador_vazio():
    with pytest.raises(ValueError):
        CredenciaisEntrada(identificador="   ", senha="senha123")
