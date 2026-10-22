"""NOVO: validações e operações da administração de grupos."""

import re

import pymysql

import repositorios.grupo as repositorio_grupos
from servicos.autorizacao import CATALOGO_PERMISSOES


class GrupoExistente(Exception):
    """NOVO: sinaliza colisão de nome/código para responder HTTP 409."""


def listar_grupos() -> list[dict]:
    """NOVO: devolve grupos configurados e permissões atribuídas."""
    return repositorio_grupos.listar_grupos()


def criar_grupo(dados: dict) -> dict:
    """NOVO: valida código e permissões antes de persistir um grupo."""
    codigo = dados["codigo"].strip().lower()
    nome = dados["nome"].strip()
    if not re.fullmatch(r"[a-z][a-z0-9_-]{1,49}", codigo):
        raise ValueError("O código deve começar por letra e usar letras, números, _ ou -.")
    if not nome:
        raise ValueError("O nome do grupo não pode ficar vazio.")
    permissoes = sorted(set(dados["permissoes"]))
    desconhecidas = set(permissoes) - CATALOGO_PERMISSOES.keys()
    if desconhecidas:
        raise ValueError(f"Permissões desconhecidas: {', '.join(sorted(desconhecidas))}.")
    if (
        repositorio_grupos.buscar_grupo_por_codigo(codigo) is not None
        or repositorio_grupos.buscar_grupo_por_nome(nome) is not None
    ):
        raise GrupoExistente("Já existe um grupo com este código ou nome.")
    try:
        return repositorio_grupos.criar_grupo(codigo, nome, permissoes)
    except pymysql.err.IntegrityError as erro:
        if erro.args and erro.args[0] == 1062:
            raise GrupoExistente(
                "Já existe um grupo com este código ou nome."
            ) from erro
        raise


def substituir_permissoes(grupo_id: int, permissoes: list[str]) -> bool:
    """NOVO: troca permissões apenas de grupos existentes."""
    grupo = repositorio_grupos.buscar_grupo_por_id(grupo_id)
    if grupo is None:
        return False
    permissoes_unicas = sorted(set(permissoes))
    desconhecidas = set(permissoes_unicas) - CATALOGO_PERMISSOES.keys()
    if desconhecidas:
        raise ValueError(f"Permissões desconhecidas: {', '.join(sorted(desconhecidas))}.")
    if grupo["codigo"] == "administrador":
        obrigatorias = {"grupos:consultar", "grupos:gerenciar", "usuarios:atribuir_grupo"}
        if not obrigatorias.issubset(permissoes_unicas):
            raise ValueError(
                "O grupo Administrador precisa manter consulta e gestão de grupos "
                "e atribuição de usuários."
            )
    repositorio_grupos.substituir_permissoes(grupo_id, permissoes_unicas)
    return True


def atribuir_usuario_ao_grupo(usuario_id: int, grupo_id: int) -> bool:
    """NOVO: associa uma conta a um grupo existente."""
    grupo = repositorio_grupos.buscar_grupo_por_id(grupo_id)
    if grupo is None:
        return False
    resultado = repositorio_grupos.atribuir_usuario_ao_grupo(usuario_id, grupo)
    if resultado == "ultimo_administrador":
        raise ValueError("Não é possível remover o último Administrador do sistema.")
    if resultado == "usuario_inexistente":
        return False
    return True
