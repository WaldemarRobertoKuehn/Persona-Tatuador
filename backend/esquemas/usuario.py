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


class TokenSaida(BaseModel):
    access_token: str
    token_type: str = "bearer"
