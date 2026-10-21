"""Rotas de cadastro e consulta dos usuários."""

from fastapi import APIRouter, HTTPException

import servicos.usuario as servico_usuarios
from esquemas.usuario import UsuarioCadastro, UsuarioSaida
from rotas.autenticacao import obter_usuario_atual
from fastapi import Depends


roteador_usuarios = APIRouter(prefix="/usuarios", tags=["usuarios"])


@roteador_usuarios.post("", response_model=UsuarioSaida, status_code=201)
def cadastrar_usuario(dados: UsuarioCadastro) -> dict:
    """Cadastra nome, email e senha; a senha é guardada somente como hash.

    Quem entra por esta rota é cliente: o papel "tatuador" é do dono e dos
    tatuadores do estúdio, e quem cria essa conta é o próprio estúdio.
    """
    usuario = servico_usuarios.cadastrar(dados.model_dump())
    if usuario is None:
        raise HTTPException(status_code=409, detail="Este email já está cadastrado.")
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "papel": usuario["papel"],
        "cliente_id": usuario["cliente_id"],
    }


@roteador_usuarios.get("/eu", response_model=UsuarioSaida)
def buscar_usuario_atual(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    """Devolve os dados públicos do usuário autenticado pelo token."""
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "papel": usuario["papel"],
        "cliente_id": usuario["cliente_id"],
    }


@roteador_usuarios.get("/{usuario_id}", response_model=UsuarioSaida)
def buscar_usuario(usuario_id: int) -> dict:
    """Busca um usuário pelo identificador ou responde 404 se não existir.

    A resposta tem o mesmo esquema da rota de cadastro, e por isso o hash da
    senha não sai daqui: o response_model corta o que não está no esquema, e o
    esquema não tem hash. Sem ele, a busca por id devolveria o hash da senha
    de qualquer conta.
    """
    usuario = servico_usuarios.buscar_por_id(usuario_id)

    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "papel": usuario["papel"],
        "cliente_id": usuario["cliente_id"],
    }
