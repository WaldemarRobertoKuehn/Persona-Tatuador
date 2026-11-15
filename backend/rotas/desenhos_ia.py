"""Rota que pede à IA uma proposta de desenho para uma tatuagem."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from jangada_ai.errors import LLMError

from esquemas.imagem import ImagemSaida
from ia.desenho import DesenhoGeradoInvalido, gerar_desenho
from rotas.dependencias import exigir_acesso_a_tatuagem, exigir_permissao
import servicos.imagem as servico_imagens


logger = logging.getLogger(__name__)

roteador_desenhos_ia = APIRouter(
    prefix="/tatuagens/{tatuagem_id}/desenho-ia",
    tags=["inteligência artificial"],
)


@roteador_desenhos_ia.post(
    "",
    response_model=ImagemSaida,
    status_code=201,
    responses={503: {"description": "Nenhum provedor de IA conseguiu desenhar."}},
)
def criar_desenho_ia(
    tatuagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("desenhos:gerar")),
) -> dict:
    """Gera e grava uma proposta pendente, sem aprová-la automaticamente."""
    try:
        conteudo = gerar_desenho(tatuagem)
    except LLMError as erro:
        logger.warning(
            "Desenho por IA indisponível: provedor=%s categoria=%s status=%s",
            erro.provider or "não identificado",
            erro.category,
            erro.status_code or "não informado",
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "A IA não conseguiu gerar o desenho agora. "
                "O pedido continua salvo; tente novamente mais tarde."
            ),
        ) from erro
    except DesenhoGeradoInvalido as erro:
        logger.warning("Desenho por IA inválido: resposta fora do formato seguro.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "A IA devolveu um desenho inválido. "
                "Tente gerar novamente ou envie um arquivo manualmente."
            ),
        ) from erro

    nome = f"desenho-ia-{tatuagem_id}.svg"
    return servico_imagens.salvar_desenho_gerado(tatuagem_id, nome, conteudo)
