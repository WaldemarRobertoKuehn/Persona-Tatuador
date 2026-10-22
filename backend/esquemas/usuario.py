"""Esquemas de entrada e saída para cadastro e login."""

import re

from pydantic import BaseModel, Field, field_validator


class UsuarioCadastro(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=8, max_length=128)

    @field_validator("nome")
    @classmethod
    def limpar_nome(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 2:
            raise ValueError("Informe um nome com pelo menos 2 caracteres.")
        return valor

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ValueError("Informe um email válido.")
        return valor


class CredenciaisEntrada(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ValueError("Informe um email válido.")
        return valor


class UsuarioSaida(BaseModel):
    id: int
    nome: str
    email: str | None
    # papel permanece por compatibilidade com a tela; a autorização usa o grupo
    # persistido e as permissões que o back carrega para a conta.
    papel: str
    # cliente_id é o elo com a tabela clientes, e ele é vazio para o tatuador.
    # A tela da cliente usa esse id para filtrar as tatuagens dela.
    cliente_id: int | None = None
    # NOVO: o código do grupo é exposto para refletir a autorização atual da conta.
    grupo_id: int
    grupo: str
    permissoes: list[str] = Field(default_factory=list)


# NOVO: esquemas das operações administrativas de grupos e associações.
class GrupoEntrada(BaseModel):
    """NOVO: campos para criar um grupo e selecionar permissões do catálogo."""

    codigo: str = Field(min_length=2, max_length=50)
    nome: str = Field(min_length=1, max_length=80)
    permissoes: list[str] = Field(default_factory=list)


class GrupoPermissoesEntrada(BaseModel):
    """NOVO: lista completa de permissões que substituirá as atuais do grupo."""

    permissoes: list[str]


class GrupoSaida(BaseModel):
    """NOVO: forma pública de um grupo com os códigos de permissão associados."""

    id: int
    codigo: str
    nome: str
    permissoes: list[str]


class AtribuicaoGrupoEntrada(BaseModel):
    """NOVO: grupo de destino para uma conta existente."""

    grupo_id: int = Field(gt=0)


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
