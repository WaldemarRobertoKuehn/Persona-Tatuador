"""Rota de login e dependência para identificar o usuário pelo token."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import seguranca
import servicos.usuario as servico_usuarios
from esquemas.usuario import CredenciaisEntrada, TokenSaida


roteador_autenticacao = APIRouter(prefix="/autenticacao", tags=["autenticacao"])
# NOVO: HTTPBearer permite colar o token obtido no login no botão Authorize do /docs.
esquema_bearer = HTTPBearer(auto_error=False)


@roteador_autenticacao.post("/login", response_model=TokenSaida)
def login(credenciais: CredenciaisEntrada) -> dict:
    """Confere email e senha e emite um token de acesso."""
    usuario = servico_usuarios.autenticar(credenciais.email, credenciais.senha)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": seguranca.gerar_token(usuario["id"]), "token_type": "bearer"}


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
) -> dict:
    """Valida o token e devolve a conta correspondente."""
    # NOVO: resposta explícita 401 preserva o comportamento para chamadas sem token.
    if credenciais is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer obrigatório.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        usuario_id = seguranca.ler_token(credenciais.credentials)
    except ValueError:
        usuario_id = None
    usuario = servico_usuarios.buscar_por_id(usuario_id) if usuario_id is not None else None
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return usuario
