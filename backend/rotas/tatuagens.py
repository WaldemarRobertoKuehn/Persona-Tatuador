"""As rotas de tatuagem.

Este arquivo é a única parte do back que conhece HTTP. Ele recebe a requisição,
entrega o que pedem ao serviço e traduz a resposta em status. Regra de cartilha
não mora aqui: a regra está no serviço, e a única decisão desta camada é dizer
qual status cabe em cada resposta.

Os status usados são os quatro da aula: 200 na leitura, 201 na criação, 404
quando a tatuagem não existe, e 422 quando o serviço recusa um passo.

Cada rota tem o response_model, que é o esquema de saída. Isso não é enfeite: sem
ele o /docs mostraria o esquema de entrada, e o front veria um campo que o back
não devolve.
"""

from fastapi import APIRouter, HTTPException, Query

import servicos.tatuagem as servico_tatuagens
from esquemas.tatuagem import TatuagemEntrada, TatuagemSaida

# O APIRouter é o conjunto de rotas de um recurso. O prefixo "/tatuagens" evita
# escrever o caminho inteiro em cada rota, e a tag é o que agrupa elas no /docs.
# Como as rotas de tatuagem são a raiz do recurso, o caminho final é "".
roteador_tatuagens = APIRouter(prefix="/tatuagens", tags=["tatuagens"])


@roteador_tatuagens.get("", response_model=list[TatuagemSaida])
def listar_tatuagens(
    etapa: str | None = Query(default=None, description="Filtra por etapa."),
    cliente_id: int | None = Query(default=None, description="Filtra por cliente."),
) -> list[dict]:
    """Lista as tatuagens, com filtro opcional por etapa e por cliente.

    Os dois filtros são parâmetros de consulta, e são opcionais: sem nenhum deles
    a API devolve tudo, que é o que a agenda do Vitor quer. Com o filtro de etapa
    a agenda mostra só uma aba, e com o filtro de cliente a tela da Bruna mostra
    só as tatuagens dela.
    """
    return servico_tatuagens.listar_tatuagens(etapa, cliente_id)


@roteador_tatuagens.post("", response_model=TatuagemSaida, status_code=201)
def pedir_tatuagem(tatuagem: TatuagemEntrada) -> dict:
    """Pede uma tatuagem nova e devolve 201, com a tatuagem já gravada.

    O parâmetro anotado com TatuagemEntrada é o corpo da requisição: o FastAPI
    lê o JSON, valida campo por campo e, se algo estiver errado, responde 422
    sozinho, antes desta função ser chamada.

    O status é 201 e não 200 porque foi criado algo novo. A etapa "pedida" não é
    passada aqui: quem decide essa etapa é o serviço, que aplica a regra.
    """
    return servico_tatuagens.pedir_tatuagem(tatuagem.model_dump())


@roteador_tatuagens.get("/{tatuagem_id}", response_model=TatuagemSaida)
def buscar_tatuagem(tatuagem_id: int) -> dict:
    """Mostra uma tatuagem, e responde 404 se o id não existir.

    O None que o serviço devolve aqui é o mesmo sinal que ele devolve quando
    recusa um passo. A tradução é outra: id que não existe é 404, e quem escreve
    isso é a rota, com HTTPException.
    """
    tatuagem = servico_tatuagens.buscar_tatuagem(tatuagem_id)

    if tatuagem is None:
        raise HTTPException(status_code=404, detail="Tatuagem não encontrada.")

    return tatuagem
