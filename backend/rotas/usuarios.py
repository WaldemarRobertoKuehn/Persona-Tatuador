"""Rotas de cadastro e consulta dos usuários."""

from fastapi import APIRouter, HTTPException

import repositorios.cliente as repositorio_clientes
import servicos.usuario as servico_usuarios
from esquemas.usuario import UsuarioCadastro, UsuarioSaida
from rotas.autenticacao import obter_usuario_atual
from fastapi import Depends


roteador_usuarios = APIRouter(prefix="/usuarios", tags=["usuarios"])


@roteador_usuarios.post("", response_model=UsuarioSaida, status_code=201)
def cadastrar_usuario(dados: UsuarioCadastro) -> dict:
    """Cadastra nome, email e senha; a senha é guardada somente como hash."""
    usuario = servico_usuarios.cadastrar(dados.model_dump())
    if usuario is None:
        raise HTTPException(status_code=409, detail="Este email já está cadastrado.")
    return {"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"]}


@roteador_usuarios.get("/eu", response_model=UsuarioSaida)
def buscar_usuario_atual(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    """Devolve os dados públicos do usuário autenticado pelo token."""
    return {"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"]}


@roteador_usuarios.get("/{usuario_id}")
def buscar_usuario(usuario_id: int) -> dict:
    """Busca um usuário pelo identificador ou responde 404 se não existir."""
    usuario = repositorio_clientes.buscar_cliente(usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario
