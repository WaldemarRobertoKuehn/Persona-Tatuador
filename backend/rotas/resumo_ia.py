"""Rota HTTP para solicitar um rascunho de resumo por IA."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jangada_ai.errors import LLMError

# Reutilizar a mesma proteção de acesso usada para consultar o histórico oficial.
from rotas.dependencias import exigir_acesso_a_tatuagem

# Manter a lógica de IA dentro de backend/ia; a rota só encaminha e traduz falhas.
from ia.sugestoes import resumir_historico


# Registrar somente metadados normalizados para ajudar a diagnosticar falhas
# sem expor mensagens do provedor, conteúdo da tatuagem ou credenciais.
logger = logging.getLogger(__name__)


# Agrupar a rota no caminho da tatuagem e documentar o recurso no /docs.
roteador_resumo_ia = APIRouter(
    prefix="/tatuagens/{tatuagem_id}/resumo-ia",
    tags=["inteligência artificial"],
)


# Disponibilizar o rascunho sem alterar o histórico oficial ou persistir a resposta.
@roteador_resumo_ia.post(
    "",
    response_model=dict[str, str],
    responses={503: {"description": "Nenhum provedor de IA conseguiu responder."}},
)
def gerar_resumo_ia(
    tatuagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "passos:listar_proprios",
            "passos:listar_todos",
        )
    ),
) -> dict[str, str]:
    """Gerar e devolver um rascunho para revisão da pessoa solicitante."""
    try:
        return {"rascunho": resumir_historico(tatuagem)}
    except LLMError as erro:
        # Registrar apenas a categoria e o provedor da última falha normalizada.
        logger.warning(
            "Resumo por IA indisponível: provedor=%s categoria=%s status=%s",
            erro.provider or "não identificado",
            erro.category,
            erro.status_code or "não informado",
        )

        # Traduzir a falha em indisponibilidade sem expor detalhes na resposta.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A IA não conseguiu gerar o resumo agora. Tente novamente mais tarde.",
        ) from erro
