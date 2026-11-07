"""Esquemas Pydantic dos metadados das imagens.

O arquivo binário não aparece aqui: a listagem devolve só o que a tela precisa
para decidir o que mostrar, e o download tem uma rota própria.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ImagemSaida(BaseModel):
    """Metadados de uma imagem, sem o conteúdo binário."""

    id: int
    tatuagem_id: int
    nome: str
    content_type: str
    tamanho_bytes: int
    tipo: str
    status: str
    criado_em: datetime
    aprovada_em: datetime | None = None
    recusada_em: datetime | None = None
    motivo_recusa: str | None = None


class ImagemRecusaEntrada(BaseModel):
    """Motivo opcional que o cliente deixa ao recusar um desenho."""

    motivo: str = Field(
        default="",
        max_length=500,
        description="O que não agradou no desenho, se o cliente quiser explicar.",
    )
