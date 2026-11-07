"""As rotas da agenda de sessões e retoques.

A disponibilidade é uma leitura separada da lista de agendamentos: a tela pede
todos os horários de um dia e recebe livre ou ocupado, sem repetir no front a
regra de expediente.

O cancelamento usa DELETE. Por isso o CORS do main precisa aceitar esse método.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from esquemas.agendamento import (
    AgendamentoEntrada,
    AgendamentoSaida,
    DisponibilidadeSaida,
)
from rotas.dependencias import exigir_acesso_a_tatuagem, exigir_permissao
import servicos.agendamento as servico_agendamentos
from servicos.excecoes import (
    AgendamentoJaCancelado,
    AgendamentoNaoEncontrado,
    AgendamentoNoPassado,
    AgendamentoDeOutroTatuador,
    DataForaDoExpediente,
    EtapaNaoPermiteAgendamento,
    HorarioForaDoExpediente,
    HorarioIndisponivel,
    TipoDeAgendamentoDesconhecido,
)

# O prefixo prende a agenda a uma tatuagem, que é quem carrega o tatuador dono
# dos horários.
roteador_agendamentos = APIRouter(
    prefix="/tatuagens/{tatuagem_id}/agendamentos",
    tags=["agendamentos"],
)


def _traduzir_erro(erro: Exception) -> None:
    """Converte a recusa do serviço no status HTTP correspondente."""
    if isinstance(
        erro,
        (
            TipoDeAgendamentoDesconhecido,
            DataForaDoExpediente,
            HorarioForaDoExpediente,
            AgendamentoNoPassado,
        ),
    ):
        raise HTTPException(status_code=422, detail=str(erro))

    if isinstance(erro, AgendamentoDeOutroTatuador):
        raise HTTPException(status_code=403, detail=str(erro))

    if isinstance(
        erro,
        (
            EtapaNaoPermiteAgendamento,
            HorarioIndisponivel,
            AgendamentoJaCancelado,
        ),
    ):
        raise HTTPException(status_code=409, detail=str(erro))

    if isinstance(erro, AgendamentoNaoEncontrado):
        raise HTTPException(status_code=404, detail=str(erro))

    raise erro


# Consultar a agenda exige a permissão de leitura e o acesso à tatuagem.
@roteador_agendamentos.get("", response_model=list[AgendamentoSaida])
def listar_agendamentos(
    tatuagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("agendamentos:consultar")),
) -> list[dict]:
    """Lista os agendamentos da tatuagem, inclusive os cancelados do histórico."""
    return servico_agendamentos.listar_agendamentos(tatuagem_id)


# A disponibilidade vem antes de qualquer rota com id para não haver dúvida de
# caminho no /docs.
@roteador_agendamentos.get(
    "/disponibilidade",
    response_model=DisponibilidadeSaida,
)
def consultar_disponibilidade(
    tatuagem_id: int,
    data: date = Query(description="O dia que a tela está mostrando."),
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("agendamentos:consultar")),
) -> dict:
    """Devolve os horários do dia, com o que está livre e o que está ocupado."""
    return servico_agendamentos.obter_disponibilidade(tatuagem, data)


# Marcar sessão ou retoque é exclusivo de quem gerencia a agenda.
@roteador_agendamentos.post("", response_model=AgendamentoSaida, status_code=201)
def agendar(
    tatuagem_id: int,
    dados: AgendamentoEntrada,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("agendamentos:gerenciar")),
) -> dict:
    """Marca o horário e devolve o agendamento já com o nome do tatuador."""
    try:
        agendamento = servico_agendamentos.agendar(
            tatuagem_id,
            tatuagem,
            usuario,
            dados.model_dump(),
        )
    except (
        TipoDeAgendamentoDesconhecido,
        EtapaNaoPermiteAgendamento,
        AgendamentoDeOutroTatuador,
        DataForaDoExpediente,
        HorarioForaDoExpediente,
        AgendamentoNoPassado,
        HorarioIndisponivel,
    ) as erro:
        _traduzir_erro(erro)

    return agendamento


# Cancelar libera o bloco para outro agendamento, mas mantém o registro no
# histórico com o status cancelado.
@roteador_agendamentos.delete("/{agendamento_id}", status_code=204)
def cancelar_agendamento(
    tatuagem_id: int,
    agendamento_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("agendamentos:gerenciar")),
) -> Response:
    """Cancela o agendamento e devolve 204."""
    try:
        servico_agendamentos.cancelar_agendamento(
            tatuagem_id,
            agendamento_id,
            tatuagem,
            usuario,
        )
    except (
        AgendamentoNaoEncontrado,
        AgendamentoDeOutroTatuador,
        AgendamentoJaCancelado,
    ) as erro:
        _traduzir_erro(erro)

    return Response(status_code=204)
