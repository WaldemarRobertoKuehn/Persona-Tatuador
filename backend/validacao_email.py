"""Validação do e-mail no cadastro de contas.

O formato sozinho não basta: endereços como "xxx@xxx.com.br" passam na expressão
regular mas não recebem mensagem nenhuma. Aqui o domínio é consultado no DNS para
confirmar que existe um servidor de e-mail (registro MX), e nomes claramente de
teste são recusados antes mesmo da consulta.

O objetivo é barrar o endereço já na hora do cadastro, e não descobrir o problema
depois, quando o e-mail de confirmação volta como erro para o remetente.
"""

import re

import dns.exception
import dns.resolver


class EmailInvalidoError(ValueError):
    """E-mail recusado no cadastro, com a mensagem pronta para a tela."""


# Partes locais usadas em testes e exemplos, que nunca pertencem a uma pessoa.
_PARTES_LOCAIS_RESERVADAS = {
    "teste",
    "testes",
    "test",
    "testando",
    "exemplo",
    "example",
    "naoexiste",
    "noemail",
    "sememail",
    "emailteste",
}

# Domínios de teste que podem até ter MX, mas não são de clientes reais.
_DOMINIOS_RESERVADOS = {
    "teste.com",
    "test.com",
    "example.com",
    "example.org",
    "example.net",
    "xxx.com",
    "xxx.com.br",
    "ccc.com.br",
    "ooo.com.br",
    "gmail.col",
}

# "xxx", "ooo", "aaa" e variações são preenchimento, não nome de caixa.
_PREENCHIMENTO = re.compile(r"^[xoa]+$", re.IGNORECASE)
_NUMERADO = re.compile(r"^(teste|test|testando|exemplo|example)\d+$", re.IGNORECASE)


def _mensagem_de_teste() -> str:
    return "Informe um e-mail real. Endereços de teste não são aceitos."


def validar_email_entregavel(email: str) -> None:
    """Recusa e-mails que não podem receber a confirmação de cadastro.

    Levanta EmailInvalidoError com uma frase que pode ir direto para a tela. A
    consulta ao DNS é feita com tempo limite curto para a rota não ficar presa.
    """
    local, dominio = email.strip().lower().rsplit("@", 1)

    if dominio in _DOMINIOS_RESERVADOS or local in _PARTES_LOCAIS_RESERVADAS:
        raise EmailInvalidoError(_mensagem_de_teste())
    if _PREENCHIMENTO.fullmatch(local) or _NUMERADO.fullmatch(local):
        raise EmailInvalidoError(_mensagem_de_teste())

    try:
        respostas = dns.resolver.resolve(dominio, "MX", lifetime=4.0)
    except dns.resolver.NXDOMAIN as erro:
        raise EmailInvalidoError("O domínio do e-mail não existe.") from erro
    except dns.resolver.NoAnswer as erro:
        raise EmailInvalidoError("O domínio do e-mail não recebe mensagens.") from erro
    except (dns.resolver.NoNameservers, dns.exception.Timeout) as erro:
        raise EmailInvalidoError(
            "Não foi possível verificar o e-mail agora. Tente novamente."
        ) from erro
    except dns.exception.DNSException as erro:
        raise EmailInvalidoError(
            "Não foi possível verificar o e-mail agora. Tente novamente."
        ) from erro

    # MX nulo é um único registro apontando para "." e significa, por definição,
    # que o domínio não aceita e-mail.
    trocas = [str(resposta.exchange).rstrip(".") for resposta in respostas]
    if not any(trocas):
        raise EmailInvalidoError("O domínio do e-mail não recebe mensagens.")
