"""Rota para simular atendimento fictício com as personas do estúdio."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jangada_ai.errors import LLMError

from esquemas.simulacao import SimulacaoStudioEntrada, SimulacaoStudioSaida
from ia.simulacao_studio import (
    RespostaDePersonaInvalida,
    simular_atendimento,
)
from rotas.dependencias import exigir_permissao


logger = logging.getLogger(__name__)

roteador_simulacao_studio = APIRouter(
    prefix="/simulacoes/studio",
    tags=["inteligência artificial"],
)


@roteador_simulacao_studio.post(
    "",
    response_model=SimulacaoStudioSaida,
    responses={503: {"description": "A simulação por IA está indisponível."}},
    dependencies=[Depends(exigir_permissao("grupos:consultar"))],
)
def criar_simulacao_studio(
    dados: SimulacaoStudioEntrada,
) -> dict[str, list[dict[str, str | int]]]:
    """Gerar as quatro etapas fictícias sem alterar dados do estúdio."""
    try:
        return {"etapas": simular_atendimento(dados.situacao)}
    except LLMError as erro:
        logger.warning(
            "Simulação por IA indisponível: provedor=%s categoria=%s status=%s",
            erro.provider or "não identificado",
            erro.category,
            erro.status_code or "não informado",
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "A IA não conseguiu concluir a simulação agora. "
                "Tente novamente mais tarde."
            ),
        ) from erro
    except RespostaDePersonaInvalida as erro:
        logger.warning("Simulação por IA inválida: resposta fora do formato esperado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "A IA não devolveu uma etapa válida. "
                "Tente gerar a simulação novamente."
            ),
        ) from erro
