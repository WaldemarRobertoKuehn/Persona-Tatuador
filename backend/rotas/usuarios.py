"""Rotas de cadastro e consulta dos usuários."""

from fastapi import APIRouter, Depends, HTTPException

import servicos.usuario as servico_usuarios
import servicos.grupo as servico_grupos
from esquemas.usuario import (
    AtribuicaoGrupoEntrada,
    DefinirUsuarioEntrada,
    UsuarioCadastro,
    UsuarioSaida,
)
from rotas.autenticacao import obter_usuario_atual, usuario_publico as _usuario_publico
from rotas.dependencias import exigir_permissao
from validacao_email import EmailInvalidoError


roteador_usuarios = APIRouter(prefix="/usuarios", tags=["usuarios"])


# NOVO: o cadastro permanece público, mas cria somente contas Cliente.
@roteador_usuarios.post("", response_model=UsuarioSaida, status_code=201)
def cadastrar_usuario(dados: UsuarioCadastro) -> dict:
    """Cadastra nome, email e senha; a senha é guardada somente como hash.

    Quem entra por esta rota é cliente: o papel "tatuador" é do dono e dos
    tatuadores do estúdio, e quem cria essa conta é o próprio estúdio.
    """
    # NOVO: cadastro público só cria contas no grupo Cliente; papel e grupo não
    # são aceitos no corpo, impedindo que uma pessoa se cadastre como admin.
    try:
        usuario = servico_usuarios.cadastrar(dados.model_dump())
    except EmailInvalidoError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    if usuario is None:
        raise HTTPException(
            status_code=409,
            detail="Este e-mail ou usuário já está cadastrado.",
        )
    usuario_criado = servico_usuarios.buscar_por_id(usuario["id"])
    if usuario_criado is None:
        raise HTTPException(status_code=500, detail="A conta criada não foi encontrada.")
    return _usuario_publico(usuario_criado)


# NOVO: o perfil autenticado exige a permissão concedida ao grupo.
@roteador_usuarios.get(
    "/eu",
    response_model=UsuarioSaida,
    dependencies=[Depends(exigir_permissao("perfil:consultar_proprio"))],
)
def buscar_usuario_atual(usuario: dict = Depends(obter_usuario_atual)) -> dict:
    """Devolve os dados públicos do usuário autenticado pelo token."""
    return _usuario_publico(usuario)


@roteador_usuarios.put("/eu/usuario", response_model=UsuarioSaida)
def definir_usuario(
    dados: DefinirUsuarioEntrada,
    usuario: dict = Depends(obter_usuario_atual),
) -> dict:
    """Define ou troca o usuário curto da conta autenticada.

    A conta antiga, que nasceu sem usuário, usa esta rota para escolher um; a
    conta nova pode trocar o que escolheu no cadastro.
    """
    if not servico_usuarios.definir_usuario(usuario["id"], dados.usuario):
        raise HTTPException(status_code=409, detail="Este usuário já está em uso.")
    atualizado = servico_usuarios.buscar_por_id(usuario["id"])
    if atualizado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return _usuario_publico(atualizado)


# A listagem da equipe é administrativa: quem cadastra e troca o responsável de
# uma tatuagem precisa das mesmas contas que a tela mostra.
@roteador_usuarios.get(
    "/tatuadores",
    response_model=list[UsuarioSaida],
    dependencies=[Depends(exigir_permissao("usuarios:atribuir_grupo"))],
)
def listar_tatuadores() -> list[dict]:
    """Lista as contas do grupo tatuador, com o nome que a tela mostra."""
    return [
        _usuario_publico(usuario)
        for usuario in servico_usuarios.listar_tatuadores()
    ]


# O cadastro de tatuador é público? Não: a rota pública cria somente cliente, e
# esta exige a permissão que só o Administrador tem.
@roteador_usuarios.post(
    "/tatuadores",
    response_model=UsuarioSaida,
    status_code=201,
    dependencies=[Depends(exigir_permissao("usuarios:atribuir_grupo"))],
)
def cadastrar_tatuador(dados: UsuarioCadastro) -> dict:
    """Cria uma conta no grupo tatuador e devolve os dados públicos dela."""
    try:
        usuario = servico_usuarios.cadastrar_tatuador(dados.model_dump())
    except EmailInvalidoError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    if usuario is None:
        raise HTTPException(
            status_code=409,
            detail="Este e-mail ou usuário já está cadastrado.",
        )
    usuario_criado = servico_usuarios.buscar_por_id(usuario["id"])
    if usuario_criado is None:
        raise HTTPException(status_code=500, detail="A conta criada não foi encontrada.")
    return _usuario_publico(usuario_criado)


# NOVO: consultar outros usuários exige permissão explícita de grupo.
@roteador_usuarios.get(
    "/{usuario_id}",
    response_model=UsuarioSaida,
    dependencies=[Depends(exigir_permissao("usuarios:consultar"))],
)
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

    return _usuario_publico(usuario)


@roteador_usuarios.put(
    "/{usuario_id}/grupo",
    response_model=UsuarioSaida,
    dependencies=[Depends(exigir_permissao("usuarios:atribuir_grupo"))],
)
def atribuir_grupo(usuario_id: int, dados: AtribuicaoGrupoEntrada) -> dict:
    """NOVO: permite ao Administrador alterar o grupo de uma conta existente."""
    try:
        atualizado = servico_grupos.atribuir_usuario_ao_grupo(
            usuario_id,
            dados.grupo_id,
        )
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro)) from erro
    if not atualizado:
        raise HTTPException(status_code=404, detail="Usuário ou grupo não encontrado.")
    usuario_atualizado = servico_usuarios.buscar_por_id(usuario_id)
    if usuario_atualizado is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return _usuario_publico(usuario_atualizado)
