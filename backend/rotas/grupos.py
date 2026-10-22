"""NOVO: API administrativa para consultar e configurar grupos de usuários."""

from fastapi import APIRouter, Depends, HTTPException

import servicos.grupo as servico_grupos
from esquemas.usuario import (
    GrupoEntrada,
    GrupoPermissoesEntrada,
    GrupoSaida,
)
from rotas.dependencias import exigir_permissao
from servicos.autorizacao import CATALOGO_PERMISSOES


# NOVO: todas as rotas deste router exigem permissões administrativas específicas.
roteador_grupos = APIRouter(prefix="/grupos", tags=["grupos"])


@roteador_grupos.get(
    "/permissoes",
    dependencies=[Depends(exigir_permissao("grupos:consultar"))],
)
def listar_permissoes_disponiveis() -> list[dict]:
    """NOVO: descreve os códigos aceitos ao configurar permissões de grupo."""
    return [
        {"codigo": codigo, "descricao": descricao}
        for codigo, descricao in CATALOGO_PERMISSOES.items()
    ]


@roteador_grupos.get(
    "",
    response_model=list[GrupoSaida],
    dependencies=[Depends(exigir_permissao("grupos:consultar"))],
)
def listar_grupos() -> list[dict]:
    """NOVO: lista grupos e as permissões concedidas a cada um."""
    return servico_grupos.listar_grupos()


@roteador_grupos.post(
    "",
    response_model=GrupoSaida,
    status_code=201,
    dependencies=[Depends(exigir_permissao("grupos:gerenciar"))],
)
def criar_grupo(dados: GrupoEntrada) -> dict:
    """NOVO: cria um grupo com permissões escolhidas do catálogo disponível."""
    try:
        return servico_grupos.criar_grupo(dados.model_dump())
    except servico_grupos.GrupoExistente as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@roteador_grupos.put(
    "/{grupo_id}/permissoes",
    response_model=GrupoSaida,
    dependencies=[Depends(exigir_permissao("grupos:gerenciar"))],
)
def atualizar_permissoes(grupo_id: int, dados: GrupoPermissoesEntrada) -> dict:
    """NOVO: substitui as permissões de um grupo existente."""
    try:
        atualizado = servico_grupos.substituir_permissoes(
            grupo_id,
            dados.permissoes,
        )
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    if not atualizado:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    grupo_atualizado = next(
        (grupo for grupo in servico_grupos.listar_grupos() if grupo["id"] == grupo_id),
        None,
    )
    if grupo_atualizado is None:
        raise HTTPException(status_code=404, detail="Grupo não encontrado.")
    return grupo_atualizado
