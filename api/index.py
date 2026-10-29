"""Vercel entrypoint for the FastAPI application."""

from collections.abc import Awaitable, Callable
from pathlib import Path
import sys

from fastapi import Request
from starlette.responses import Response

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from main import app


@app.middleware("http")
async def remover_prefixo_da_api(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    escopo = request.scope
    caminho = escopo["path"]

    if caminho.startswith("/api/"):
        escopo["path"] = caminho[len("/api") :]
        escopo["raw_path"] = escopo["raw_path"][len(b"/api") :]

    return await call_next(request)
