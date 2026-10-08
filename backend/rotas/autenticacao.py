"""Rota de login e dependência para identificar o usuário pelo token."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import seguranca
import servicos.usuario as servico_usuarios
from esquemas.usuario import CredenciaisEntrada, TokenSaida


roteador_autenticacao = APIRouter(prefix="/autenticacao", tags=["autenticacao"])
esquema_bearer = OAuth2PasswordBearer(tokenUrl="/autenticacao/login")


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


def obter_usuario_atual(token: str = Depends(esquema_bearer)) -> dict:
    """Valida o token e devolve a conta correspondente."""
    try:
        usuario_id = seguranca.ler_token(token)
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
