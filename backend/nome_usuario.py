"""Transforma o nome da pessoa no identificador curto usado para entrar.

O login aceita o e-mail ou este identificador. Ele nasce do nome porque o
cadastro não pede um campo novo: "Fábio Boeing" vira "fabio.boeing". Quando o
nome repete, o sufixo numérico mantém o identificador único, e o login continua
sem ambiguidade.
"""

import re
import unicodedata

TAMANHO_MAXIMO = 50


def transformar_em_usuario(nome: str) -> str:
    """Converte "Fábio Boeing" em "fabio.boeing"."""
    normalizado = unicodedata.normalize("NFKD", nome or "")
    normalizado = normalizado.encode("ascii", "ignore").decode("ascii")
    normalizado = normalizado.lower()
    normalizado = re.sub(r"[^a-z0-9]+", ".", normalizado)
    normalizado = re.sub(r"\.+", ".", normalizado).strip(".")
    return normalizado[:TAMANHO_MAXIMO] or "usuario"


def gerar_usuario_unico(nome: str, existe) -> str:
    """Devolve um identificador livre, acrescentando número quando o nome repete.

    `existe` é uma função que recebe o candidato e devolve True quando ele já
    pertence a outra conta.
    """
    base = transformar_em_usuario(nome)
    candidato = base
    numero = 2

    while existe(candidato):
        sufixo = str(numero)
        candidato = f"{base[: TAMANHO_MAXIMO - len(sufixo)]}{sufixo}"
        numero += 1

    return candidato
