"""Rota HTTP para solicitar um rascunho de resumo por IA."""

from fastapi import APIRouter, Depends, HTTPException, status
from jangada_ai.errors import LLMError

# Reutilizar a mesma proteção de acesso usada para consultar o histórico oficial.
from rotas.dependencias import exigir_acesso_a_tatuagem

# Manter a lógica de IA dentro de backend/ia; a rota só encaminha e traduz falhas.
from ia.sugestoes import resumir_historico


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
        # Traduzir falhas normalizadas do Jangada em indisponibilidade, sem
        # expor detalhes de provedores, configurações ou credenciais na resposta.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A IA não conseguiu gerar o resumo agora. Tente novamente mais tarde.",
        ) from erro
