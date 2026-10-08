"""Regras de cadastro, busca e validação de contas de usuário."""

import repositorios.cliente as repositorio_clientes
import seguranca


def cadastrar(dados: dict) -> dict | None:
    """Cria uma conta ou devolve None quando o email já está cadastrado."""
    email = dados["email"].strip().lower()
    if repositorio_clientes.buscar_por_email(email) is not None:
        return None
    senha_hash = seguranca.gerar_hash(dados["senha"])
    try:
        return repositorio_clientes.criar_usuario(dados["nome"].strip(), email, senha_hash)
    except Exception as erro:
        # Trata a corrida em que duas requisições tentam cadastrar o mesmo email.
        if getattr(erro, "errno", None) == 1062:
            return None
        raise


def autenticar(email: str, senha: str) -> dict | None:
    """Devolve a conta quando o email e a senha conferem."""
    usuario = repositorio_clientes.buscar_por_email(email.strip().lower())
    if usuario is None or not usuario.get("senha_hash"):
        return None
    if not seguranca.verificar_senha(senha, usuario["senha_hash"]):
        return None
    return usuario


def buscar_por_id(usuario_id: int) -> dict | None:
    return repositorio_clientes.buscar_usuario_por_id(usuario_id)
