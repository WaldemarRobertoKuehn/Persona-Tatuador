"""Esquemas do cadastro presencial de clientes."""

from pydantic import BaseModel, Field


class ClienteEntrada(BaseModel):
    """O nome que o administrador digita no balcão."""

    nome: str = Field(
        min_length=2,
        max_length=100,
        description="Nome da cliente atendida no estúdio.",
    )


class ClienteSaida(BaseModel):
    """A cliente como a tela de administração precisa vê-la."""

    id: int
    nome: str
