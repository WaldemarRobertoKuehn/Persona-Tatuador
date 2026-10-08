"""Hash de senhas e emissão/validação de tokens de acesso."""

import base64
import hashlib
import hmac
import json
import time

from pwdlib import PasswordHash

import configuracao

hasher = PasswordHash.recommended()


def gerar_hash(senha: str) -> str:
    return hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return hasher.verify(senha, senha_hash)


def gerar_token(usuario_id: int) -> str:
    """Gera um JWT assinado com HMAC-SHA256, sem guardar dados secretos no token."""
    agora = int(time.time())
    cabecalho = {"alg": "HS256", "typ": "JWT"}
    conteudo = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + configuracao.validade_token_segundos(),
    }
    parte_cabecalho = _codificar_json(cabecalho)
    parte_conteudo = _codificar_json(conteudo)
    mensagem = f"{parte_cabecalho}.{parte_conteudo}"
    assinatura = hmac.new(
        configuracao.segredo_token().encode("utf-8"),
        mensagem.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{mensagem}.{_codificar(assinatura)}"


def ler_token(token: str) -> int:
    """Valida assinatura e validade e devolve o identificador do usuário."""
    try:
        parte_cabecalho, parte_conteudo, parte_assinatura = token.split(".")
        cabecalho = json.loads(_decodificar(parte_cabecalho))
        conteudo = json.loads(_decodificar(parte_conteudo))
        if cabecalho.get("alg") != "HS256":
            raise ValueError("Algoritmo inválido.")
        mensagem = f"{parte_cabecalho}.{parte_conteudo}"
        esperada = hmac.new(
            configuracao.segredo_token().encode("utf-8"),
            mensagem.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(esperada, _decodificar(parte_assinatura)):
            raise ValueError("Assinatura inválida.")
        if int(conteudo["exp"]) <= int(time.time()):
            raise ValueError("Token expirado.")
        return int(conteudo["sub"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as erro:
        raise ValueError("Token inválido ou expirado.") from erro


def _codificar_json(valor: dict) -> str:
    return _codificar(json.dumps(valor, separators=(",", ":")).encode("utf-8"))


def _codificar(valor: bytes) -> str:
    return base64.urlsafe_b64encode(valor).rstrip(b"=").decode("ascii")


def _decodificar(valor: str) -> bytes:
    return base64.urlsafe_b64decode(valor + "=" * (-len(valor) % 4))
