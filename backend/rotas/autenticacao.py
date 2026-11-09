"""Rota de login e dependência para identificar o usuário pelo token."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import seguranca
import configuracao
import servicos.usuario as servico_usuarios
from esquemas.usuario import (
    AlterarSenhaEntrada,
    CredenciaisEntrada,
    EmailRedefinicaoEntrada,
    RedefinirSenhaEntrada,
    TokenSaida,
)


roteador_autenticacao = APIRouter(prefix="/autenticacao", tags=["autenticacao"])
# NOVO: HTTPBearer permite colar o token obtido no login no botão Authorize do /docs.
esquema_bearer = HTTPBearer(auto_error=False)


def usuario_publico(usuario: dict) -> dict:
    """Mantém a resposta de conta sem devolver o hash de senha."""
    return {
        "id": usuario["id"],
        "nome": usuario["nome"],
        "email": usuario["email"],
        "usuario": usuario["usuario"],
        "papel": usuario["papel"],
        "cliente_id": usuario["cliente_id"],
        "grupo_id": usuario["grupo_id"],
        "grupo": usuario["grupo_codigo"],
        "permissoes": usuario.get("permissoes", []),
    }


@roteador_autenticacao.post("/login", response_model=TokenSaida)
def login(credenciais: CredenciaisEntrada) -> dict:
    """Confere e-mail/usuário e senha, emite o token e devolve a conta.

    A conta vai junto para o front não precisar de um segundo pedido a
    /usuarios/eu logo depois do login.
    """
    usuario = servico_usuarios.autenticar(
        credenciais.identificador,
        credenciais.senha,
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail, usuário ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": seguranca.gerar_token(usuario["id"]),
        "token_type": "bearer",
        "usuario": usuario_publico(usuario),
    }


@roteador_autenticacao.post("/esqueci-senha", status_code=status.HTTP_202_ACCEPTED)
def solicitar_redefinicao(dados: EmailRedefinicaoEntrada) -> dict:
    """Solicita email de redefinição sem confirmar se o endereço está cadastrado.

    O envio acontece antes da resposta, e não em BackgroundTasks, porque no
    Vercel a função é congelada assim que responde e o email se perderia.
    """
    if configuracao.configuracao_smtp() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A redefinição por email ainda não está configurada.",
        )
    servico_usuarios.solicitar_redefinicao_senha(dados.email)
    return {
        "detail": "Se houver uma conta com este email, enviaremos um link de redefinição."
    }


@roteador_autenticacao.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenhaEntrada) -> dict:
    """Troca a senha com um token válido enviado para o email da conta."""
    if not servico_usuarios.redefinir_senha(dados.token, dados.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este link é inválido ou expirou. Solicite uma nova redefinição.",
        )
    return {"detail": "Senha redefinida com sucesso."}


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


@roteador_autenticacao.post("/alterar-senha")
def alterar_senha(
    dados: AlterarSenhaEntrada,
    usuario: dict = Depends(obter_usuario_atual),
) -> dict:
    """Troca a senha da sessão atual após conferir a senha anterior."""
    if not servico_usuarios.alterar_senha(
        usuario["id"], dados.senha_atual, dados.nova_senha
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta.",
        )
    return {"detail": "Senha alterada com sucesso."}
