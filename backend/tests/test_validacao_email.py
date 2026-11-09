import dns.resolver
import pytest
from pydantic import ValidationError

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


def test_cadastro_recusa_email_de_teste():
    with pytest.raises(ValidationError, match="Endere"):
        UsuarioCadastro(nome="Ana", email="xxx@dominio-real.com", senha="senha123")


def test_cadastro_aceita_email_com_mx(monkeypatch):
    monkeypatch.setattr(
        dns.resolver,
        "resolve",
        lambda *args, **kwargs: [RespostaMx("mx1.exemplo-real.com.")],
    )

    dados = UsuarioCadastro(
        nome="Ana",
        email="ANA@Exemplo-Real.com",
        senha="senha123",
    )

    assert dados.email == "ana@exemplo-real.com"
