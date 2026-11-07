"""As decisões sobre tatuagem.

Este arquivo é a camada que pensa. Ele recebe o que a rota traz, chama o
repositório e devolve o que a rota precisa mostrar. É aqui que mora a regra da
cartilha que diz que a tatuagem nova começa pedida.

O que este arquivo não faz: não escolhe o status HTTP, porque isso é da rota, e
não levanta exceção quando a regra recusa, porque a regra recusa devolvendo um
motivo, e quem transforma o motivo em 422 é a rota.
"""

import psycopg2
from psycopg2 import errorcodes

import repositorios.tatuagem as repositorio_tatuagens
import repositorios.usuario as repositorio_usuarios
from servicos.excecoes import AgendamentoConflitante


def listar_tatuagens(etapa: str | None, cliente_id: int | None) -> list[dict]:
    """Devolve as tatuagens do sistema, com os filtros que a rota recebeu.

    A rota passa os dois filtros sempre, mesmo quando o front não mandou nenhum,
    e neste caso eles chegam como None. Passar None para a lista é o que faz o
    depósito devolver tudo, então não há nada a decidir aqui.

    O nome da cliente vem junto na mesma consulta, com JOIN, para não abrir uma
    consulta por tatuagem.
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

    O tatuador padrão também é uma decisão daqui: a tela da cliente não escolhe
    profissional, mas a agenda precisa de um responsável para abrir. Se o
    estúdio ainda não tiver tatuador, o campo fica vazio e o administrador
    atribui depois.
    """
    return repositorio_tatuagens.criar_tatuagem(
        {
            **dados,
            "etapa": "pedida",
            "tatuador_id": repositorio_usuarios.buscar_tatuador_padrao_id(),
        }
    )


def atribuir_tatuador(tatuagem_id: int, tatuador_id: int) -> dict | None:
    """Troca o tatuador responsável por uma tatuagem existente.

    O usuário de destino precisa estar no grupo tatuador. Quando não está, o
    ValueError é a recusa que a rota traduz em 422, no mesmo lugar em que o
    Pydantic recusaria um campo inválido.

    Os horários já marcados acompanham a tatuagem, porque a agenda é do
    profissional. Se o novo tatuador já atende em um desses horários, a troca é
    recusada por inteiro, e o administrador precisa cancelar ou remarcar o
    agendamento que colide antes de tentar de novo.
    """
    tatuador = repositorio_usuarios.buscar_tatuador_por_id(tatuador_id)
    if tatuador is None:
        raise ValueError("O tatuador informado não existe neste estúdio.")

    try:
        resultado, detalhe = repositorio_tatuagens.atualizar_tatuador(
            tatuagem_id,
            tatuador_id,
        )
    except psycopg2.IntegrityError as erro:
        # A corrida entre a conferência acima e a gravação é barrada pelo índice
        # único de (tatuador, data, hora_inicio). O rollback do cursor desfaz a
        # troca inteira, e a resposta é a mesma da conferência.
        if erro.pgcode == errorcodes.UNIQUE_VIOLATION:
            raise AgendamentoConflitante(
                "O tatuador escolhido já tem uma sessão marcada em um dos "
                "horários desta tatuagem. Cancele ou remarque o outro "
                "agendamento antes de trocar o responsável."
            ) from erro
        raise

    if resultado == "nao_encontrada":
        return None

    if resultado == "conflito":
        raise AgendamentoConflitante(
            f"O tatuador {tatuador['nome']} já tem sessão em "
            f"{detalhe['data'].strftime('%d/%m/%Y')} às "
            f"{detalhe['hora_inicio'].strftime('%H:%M')}. Cancele ou remarque "
            "esse horário antes de trocar o responsável."
        )

    return detalhe
