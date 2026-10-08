"""Rotas de consulta dos usuários cadastrados como clientes."""

from fastapi import APIRouter, HTTPException

import repositorios.cliente as repositorio_clientes


roteador_usuarios = APIRouter(prefix="/usuarios", tags=["usuarios"])


@roteador_usuarios.get("/{usuario_id}")
def buscar_usuario(usuario_id: int) -> dict:
    """Busca um usuário pelo identificador ou responde 404 se não existir."""
    usuario = repositorio_clientes.buscar_cliente(usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario
