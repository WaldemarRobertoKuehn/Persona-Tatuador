"""As rotas de passo.

Este arquivo é a parte do back que registra e mostra o histórico de passos de uma
tatuagem. Ele tem duas rotas só, e elas ficam aninhadas no caminho da tatuagem,
porque um passo sem tatuagem dona não existe: o caminho
"/tatuagens/{tatuagem_id}/passos" diz de quem é o passo, e é por isso que a
tatuagem não vem no corpo da requisição.

A tradução do sinal do serviço em status é o que há de mais importante aqui. O
serviço devolve três coisas diferentes:

    dict  -> o passo entrou, e a rota responde 201
    str   -> a regra da cartilha recusou, e a rota responde 422 com o motivo
    None  -> a tatuagem não existe, e a rota responde 404

O serviço não levanta HTTPException, então todo o 404 e todo o 422 deste arquivo
são escritos aqui.
"""

from fastapi import APIRouter, HTTPException

import servicos.passo as servico_passos
import servicos.tatuagem as servico_tatuagens
from esquemas.passo import PassoEntrada, PassoSaida

# O prefixo é "/tatuagens/{tatuagem_id}/passos" e não só "/passos", porque o
# histórico é sempre o de uma tatuagem. A tag é o que agrupa as duas rotas no
# /docs, ao lado das rotas de tatuagem.
roteador_passos = APIRouter(prefix="/tatuagens/{tatuagem_id}/passos", tags=["passos"])


@roteador_passos.get("", response_model=list[PassoSaida])
def listar_passos(tatuagem_id: int) -> list[dict]:
    """Mostra o histórico de passos de uma tatuagem, na ordem em que entraram.

    Antes de listar, confirma que a tatuagem existe. Se ela não existir, a lista
    viria vazia e o front não distinguiria "sem passos" de "tatuagem errada", que
    são coisas diferentes para quem está lendo um histórico.

    O tatuagem_id da função é o mesmo {tatuagem_id} do prefixo: o FastAPI
    preenche o parâmetro com o que veio no caminho, e ainda confere se é número.
    """
    tatuagem = servico_tatuagens.buscar_tatuagem(tatuagem_id)

    if tatuagem is None:
        raise HTTPException(status_code=404, detail="Tatuagem não encontrada.")

    return servico_passos.listar_passos(tatuagem_id)


@roteador_passos.post("", response_model=PassoSaida, status_code=201)
def registrar_passo(tatuagem_id: int, passo: PassoEntrada) -> dict:
    """Registra um passo numa tatuagem, se a regra da cartilha aceitar.

    O parâmetro tatuagem_id vem do caminho, e o passo vem do corpo: o corpo é só o
    tipo e a observação, porque de qual tatuagem é o passo já está no caminho.

    O isinstance com str é o que separa os três retornos do serviço. Se o que
    voltou é texto, é o motivo da recusa da regra, e a resposta é 422 com esse
    texto no detalhe, para o Vitor ler o que deu errado. Se voltou None, a
    tatuagem não existe, e a resposta é 404. Se voltou dicionário, deu certo, e a
    resposta é 201 com o passo gravado.
    """
    resultado = servico_passos.registrar_passo(tatuagem_id, passo.model_dump())

    if resultado is None:
        raise HTTPException(status_code=404, detail="Tatuagem não encontrada.")

    if isinstance(resultado, str):
        raise HTTPException(status_code=422, detail=resultado)

    return resultado
