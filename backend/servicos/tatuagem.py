"""As decisões sobre tatuagem.

Este arquivo é a camada que pensa. Ele recebe o que a rota traz, chama o
repositório e devolve o que a rota precisa mostrar. É aqui que mora a regra da
cartilha que diz que a tatuagem nova começa pedida.

O que este arquivo não faz: não escolhe o status HTTP, porque isso é da rota, e
não levanta exceção quando a regra recusa, porque a regra recusa devolvendo um
motivo, e quem transforma o motivo em 422 é a rota.
"""

import repositorios.tatuagem as repositorio_tatuagens


def listar_tatuagens(etapa: str | None, cliente_id: int | None) -> list[dict]:
    """Devolve as tatuagens do sistema, com os filtros que a rota recebeu.

    A rota passa os dois filtros sempre, mesmo quando o front não mandou nenhum,
    e neste caso eles chegam como None. Passar None para a lista é o que faz o
    depósito devolver tudo, então não há nada a decidir aqui.
    """
    return repositorio_tatuagens.listar_tatuagens(etapa, cliente_id)


def buscar_tatuagem(tatuagem_id: int) -> dict | None:
    """Devolve uma tatuagem, ou None se ela não existir.

    O None volta como está, e a rota é quem responde 404. O serviço não escolhe
    status.
    """
    return repositorio_tatuagens.buscar_tatuagem(tatuagem_id)


def pedir_tatuagem(dados: dict) -> dict:
    """Cria a tatuagem pedida pela Bruna e devolve como ela foi gravada.

    Esta é a única decisão deste arquivo: a tatuagem nasce pedida. A regra está
    escrita na cartilha, e é por isso que ela fica aqui e não no repositório,
    que é só o depósito.

    O ** dados junta o que a rota mandou com a etapa inicial, num dicionário
    novo. Assim o depósito recebe o registro completo, e o repositório não
    precisa saber de onde veio cada campo.
    """
    return repositorio_tatuagens.criar_tatuagem({**dados, "etapa": "pedida"})
