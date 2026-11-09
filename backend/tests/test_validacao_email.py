import dns.resolver
import pytest
from pydantic import ValidationError

import repositorios.cliente as repositorio_clientes
import repositorios.grupo as repositorio_grupos
import repositorios.usuario as repositorio_usuarios
import servicos.usuario as servico_usuarios
import validacao_email
from esquemas.usuario import UsuarioCadastro
from validacao_email import EmailInvalidoError, validar_email_entregavel


class RespostaMx:
    def __init__(self, exchange):
        self.exchange = exchange


def _sem_dns(*args, **kwargs):
    raise AssertionError("o DNS não deveria ser consultado para este e-mail")


def test_recusa_preenchimento_sem_consultar_dns(monkeypatch):
    monkeypatch.setattr(dns.resolver, "resolve", _sem_dns)

    with pytest.raises(EmailInvalidoError):
        validar_email_entregavel("xxx@dominio-real.com")


def test_recusa_dominio_reservado_sem_consultar_dns(monkeypatch):
    monkeypatch.setattr(dns.resolver, "resolve", _sem_dns)

    with pytest.raises(EmailInvalidoError):
        validar_email_entregavel("ana@teste.com")


def test_recusa_dominio_sem_mx(monkeypatch):
    def sem_mx(*args, **kwargs):
        raise dns.resolver.NoAnswer

    monkeypatch.setattr(dns.resolver, "resolve", sem_mx)

    with pytest.raises(EmailInvalidoError, match="não recebe mensagens"):
        validar_email_entregavel("ana@sem-mx.com.br")


def test_recusa_dominio_inexistente(monkeypatch):
    def inexistente(*args, **kwargs):
        raise dns.resolver.NXDOMAIN

    monkeypatch.setattr(dns.resolver, "resolve", inexistente)

    with pytest.raises(EmailInvalidoError, match="não existe"):
        validar_email_entregavel("ana@nao-existe.com")


def test_recusa_mx_nulo(monkeypatch):
    monkeypatch.setattr(
        dns.resolver,
        "resolve",
        lambda *args, **kwargs: [RespostaMx(".")],
    )

    with pytest.raises(EmailInvalidoError, match="não recebe mensagens"):
        validar_email_entregavel("ana@dominio-nulo.com.br")


def test_aceita_dominio_com_mx(monkeypatch):
    monkeypatch.setattr(
        dns.resolver,
        "resolve",
        lambda *args, **kwargs: [RespostaMx("mx1.exemplo-real.com.")],
    )

    validar_email_entregavel("ana@exemplo-real.com")


def test_cadastro_nao_grava_quando_email_e_invalido(monkeypatch):
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_email", lambda _: None)
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_usuario", lambda _: None)

    def recusar(_):
        raise EmailInvalidoError("Informe um e-mail real.")

    monkeypatch.setattr(validacao_email, "validar_email_entregavel", recusar)

    def nao_gravar(*args, **kwargs):
        raise AssertionError("nada deveria ser gravado no banco")

    monkeypatch.setattr(repositorio_clientes, "criar_cliente", nao_gravar)
    monkeypatch.setattr(repositorio_usuarios, "criar_usuario", nao_gravar)

    with pytest.raises(EmailInvalidoError):
        servico_usuarios.cadastrar(
            {
                "nome": "Ana",
                "email": "xxx@dominio-real.com",
                "usuario": "ana",
                "senha": "senha123",
            }
        )


def test_cadastro_grava_quando_email_e_valido(monkeypatch):
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_email", lambda _: None)
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_usuario", lambda _: None)
    monkeypatch.setattr(validacao_email, "validar_email_entregavel", lambda _: None)
    monkeypatch.setattr(servico_usuarios.seguranca, "gerar_hash", lambda _: "hash")
    monkeypatch.setattr(
        repositorio_grupos,
        "buscar_grupo_por_codigo",
        lambda _: {"id": 1, "codigo": "cliente"},
    )

    cliente_criado = {}

    def criar_cliente(nome):
        cliente_criado["id"] = 10
        return 10

    def criar_usuario(nome, email, senha, papel, cliente_id, grupo_id, usuario):
        return {
            "id": 1,
            "nome": nome,
            "email": email,
            "usuario": usuario,
            "papel": papel,
            "cliente_id": cliente_id,
            "grupo_id": grupo_id,
            "grupo_codigo": papel,
            "permissoes": [],
        }

    monkeypatch.setattr(repositorio_clientes, "criar_cliente", criar_cliente)
    monkeypatch.setattr(repositorio_usuarios, "criar_usuario", criar_usuario)
    monkeypatch.setattr(servico_usuarios, "_notificar_conta_criada", lambda _: None)

    usuario = servico_usuarios.cadastrar(
        {
            "nome": "Ana",
            "email": "ana@exemplo-real.com",
            "usuario": "ana",
            "senha": "senha123",
        }
    )

    assert usuario["email"] == "ana@exemplo-real.com"
    assert usuario["usuario"] == "ana"
    assert cliente_criado["id"] == 10


def test_cadastro_recusa_usuario_repetido(monkeypatch):
    monkeypatch.setattr(repositorio_usuarios, "buscar_por_email", lambda _: None)
    monkeypatch.setattr(
        repositorio_usuarios,
        "buscar_por_usuario",
        lambda _: {"id": 2, "usuario": "ana"},
    )

    def nao_gravar(*args, **kwargs):
        raise AssertionError("nada deveria ser gravado no banco")

    monkeypatch.setattr(repositorio_clientes, "criar_cliente", nao_gravar)
    monkeypatch.setattr(repositorio_usuarios, "criar_usuario", nao_gravar)

    usuario = servico_usuarios.cadastrar(
        {
            "nome": "Ana",
            "email": "ana@exemplo-real.com",
            "usuario": "ana",
            "senha": "senha123",
        }
    )

    assert usuario is None


def test_esquema_recusa_formato_invalido():
    with pytest.raises(ValidationError):
        UsuarioCadastro(
            nome="Ana",
            email="sem-arroba",
            usuario="ana",
            senha="senha123",
        )


def test_esquema_recusa_usuario_invalido():
    with pytest.raises(ValidationError):
        UsuarioCadastro(
            nome="Ana",
            email="ana@exemplo-real.com",
            usuario="Ana com espaço",
            senha="senha123",
        )


def test_esquema_normaliza_email():
    dados = UsuarioCadastro(
        nome="Ana",
        email="ANA@Exemplo-Real.com",
        usuario="ana",
        senha="senha123",
    )

    assert dados.email == "ana@exemplo-real.com"


def test_esquema_normaliza_usuario():
    dados = UsuarioCadastro(
        nome="Ana",
        email="ana@exemplo-real.com",
        usuario="  Ana.Silva  ",
        senha="senha123",
    )

    assert dados.usuario == "ana.silva"
