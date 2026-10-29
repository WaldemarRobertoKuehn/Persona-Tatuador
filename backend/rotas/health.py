"""Rota simples para confirmar que a API está no ar."""

from fastapi import APIRouter

roteador_health = APIRouter(tags=["health"])


@roteador_health.get("/")
def verificar_saude() -> dict[str, str]:
    """Informa que a API está respondendo."""
    return {"status": "ok"}
