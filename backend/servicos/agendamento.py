"""A regra da agenda de sessões e retoques.

O expediente, o bloqueio por tatuador e a etapa em que a tatuagem pode ser
agendada ficam aqui. A agenda é do tatuador: dois tatuadores podem atender no
mesmo horário, mas o mesmo tatuador não pode ter dois agendamentos ativos no
mesmo bloco de uma hora.

O fuso é fixo em UTC-3 porque o estúdio fica em São Paulo e o horário de verão
não é mais usado no Brasil. Isso evita depender da base de fusos do sistema.
"""

from datetime import date as date_type
from datetime import datetime, time, timedelta, timezone

import repositorios.agendamento as repositorio_agendamentos
from servicos.excecoes import (
    AgendamentoJaCancelado,
    AgendamentoNaoEncontrado,
    AgendamentoNoPassado,
    AgendamentoDeOutroTatuador,
    DataForaDoExpediente,
    EtapaNaoPermiteAgendamento,
    HorarioForaDoExpediente,
    HorarioIndisponivel,
    TatuagemSemTatuador,
    TipoDeAgendamentoDesconhecido,
)


# Fuso fixo do estúdio. O Brasil não usa mais horário de verão desde 2019.
FUSO_ESTUDIO = timezone(timedelta(hours=-3))

# Cada atendimento ocupa uma hora. A hora de fim é sempre calculada, nunca vem
# do front, para não existir agendamento de duração diferente.
DURACAO = timedelta(hours=1)

# Horários de início aceitos na semana e no sábado. As pausas de almoço e entre
# turnos não aparecem porque não são horários de começo.
HORARIOS_DE_SEMANA = [
    time(8, 30),
    time(9, 30),
    time(10, 30),
    time(13, 30),
    time(14, 30),
    time(15, 30),
    time(16, 30),
    time(17, 30),
]

HORARIOS_DE_SABADO = [
    time(8, 0),
    time(9, 0),
    time(10, 0),
    time(11, 0),
]

# A tatuagem só entra na agenda depois do desenho aprovado e enquanto ainda está
# recebendo sessões. "finalizada" não agenda mais nada.
ETAPAS_QUE_AGENDAM = {"desenho aprovado", "em sessões"}


def _agora() -> datetime:
    """Devolve o instante atual no fuso do estúdio."""
    return datetime.now(FUSO_ESTUDIO)


def _horarios_do_dia(dia_semana: int) -> list[time]:
    """Devolve os inícios de bloco de um dia da semana.

    O weekday do Python começa em segunda-feira (0) e termina no domingo (6).
    """
    if 0 <= dia_semana <= 4:
        return HORARIOS_DE_SEMANA

    if dia_semana == 5:
        return HORARIOS_DE_SABADO

    return []


def _normalizar_hora(hora: time) -> time:
    """Zera segundos e fuso para comparar com os horários da tabela."""
    return hora.replace(second=0, microsecond=0, tzinfo=None)


def _hora_fim(hora_inicio: time) -> time:
    """Devolve o fim do bloco de uma hora que começa em hora_inicio."""
    inicio = datetime.combine(date_type.min, hora_inicio)
    return (inicio + DURACAO).time()


def _validar_tipo(tipo: str) -> str:
    """Confere o tipo e devolve a grafia que fica gravada no banco."""
    normalizado = (tipo or "").strip().lower()

    # Aceita "sessao" sem til para não quebrar um cliente que digite assim, mas
    # guarda sempre "sessão", igual ao tipo do passo.
    if normalizado in ("sessão", "sessao"):
        return "sessão"

    if normalizado == "retoque":
        return "retoque"

    raise TipoDeAgendamentoDesconhecido(
        f"'{tipo}' não é um tipo de agendamento aceito. "
        "Use 'sessão' ou 'retoque'."
    )


def _validar_horario(data: date_type, hora_inicio: time) -> time:
    """Confere data, expediente e horário, e devolve a hora de fim do bloco."""
    horarios = _horarios_do_dia(data.weekday())

    if not horarios:
        raise DataForaDoExpediente(
            "O estúdio não atende nesse dia. A agenda abre de segunda a sábado."
        )

    if hora_inicio not in horarios:
        raise HorarioForaDoExpediente(
            "Esse horário não faz parte do expediente. "
            "Escolha um dos horários mostrados na agenda."
        )

    inicio = datetime.combine(data, hora_inicio, tzinfo=FUSO_ESTUDIO)

    # Não adianta marcar um horário que já começou. A comparação usa o relógio
    # do estúdio, e não o do navegador.
    if inicio <= _agora():
        raise AgendamentoNoPassado(
            "Esse horário já passou. Escolha um horário futuro."
        )

    return _hora_fim(hora_inicio)


def obter_disponibilidade(tatuagem: dict | None, data: date_type) -> dict:
    """Devolve todos os horários do dia, com o que está livre e o que está ocupado.

    O dia fechado também volta como resposta: a tela mostra "fechado" em vez de
    fingir que a data não existe.
    """
    horarios = _horarios_do_dia(data.weekday())

    if tatuagem is None:
        return {
            "data": data,
            "aberto": False,
            "horarios": [],
            "motivo": "Tatuagem não encontrada.",
        }

    if not horarios:
        return {
            "data": data,
            "aberto": False,
            "horarios": [],
            "motivo": "O estúdio não atende nesse dia.",
        }

    tatuador_id = tatuagem.get("tatuador_id")
    if tatuador_id is None:
        return {
            "data": data,
            "aberto": False,
            "horarios": [],
            "motivo": (
                "A tatuagem ainda não tem tatuador responsável. "
                "O administrador precisa atribuir um profissional."
            ),
        }

    ocupados = repositorio_agendamentos.listar_ativos_do_tatuador(
        tatuador_id,
        data,
    )

    # O mapa troca a lista por uma consulta direta por horário. O id fica junto
    # para a tela poder marcar o bloco que já tem agendamento.
    por_horario = {
        agendamento["hora_inicio"]: agendamento["id"]
        for agendamento in ocupados
    }

    agora = _agora()
    saida = []

    for hora_inicio in horarios:
        inicio = datetime.combine(data, hora_inicio, tzinfo=FUSO_ESTUDIO)
        agendamento_id = por_horario.get(hora_inicio)
        disponivel = agendamento_id is None and inicio > agora

        saida.append(
            {
                "hora_inicio": hora_inicio,
                "hora_fim": _hora_fim(hora_inicio),
                "disponivel": disponivel,
                "agendamento_id": agendamento_id,
            }
        )

    return {"data": data, "aberto": True, "horarios": saida, "motivo": None}


def listar_agendamentos(tatuagem_id: int) -> list[dict]:
    """Devolve a agenda de uma tatuagem, do horário mais antigo ao mais novo."""
    return repositorio_agendamentos.listar_agendamentos(tatuagem_id)


def agendar(
    tatuagem_id: int,
    tatuagem: dict | None,
    usuario: dict,
    dados: dict,
) -> dict | None:
    """Marca uma sessão ou o retoque na agenda do tatuador da tatuagem."""
    if tatuagem is None:
        return None

    if tatuagem["etapa"] not in ETAPAS_QUE_AGENDAM:
        raise EtapaNaoPermiteAgendamento(
            "Só dá para agendar depois do desenho aprovado e antes de finalizar. "
            f"Esta tatuagem está '{tatuagem['etapa']}'."
        )

    tatuador_id = tatuagem.get("tatuador_id")
    if tatuador_id is None:
        raise TatuagemSemTatuador(
            "A tatuagem ainda não tem tatuador responsável. "
            "O administrador precisa atribuir um profissional antes de agendar."
        )

    # A agenda é do tatuador responsável. Outro tatuador não marca horário na
    # agenda de um colega, mesmo tendo a permissão geral de gerenciar.
    if usuario["papel"] == "tatuador" and usuario["id"] != tatuador_id:
        raise AgendamentoDeOutroTatuador(
            "A agenda desta tatuagem pertence a outro tatuador."
        )

    tipo = _validar_tipo(dados["tipo"])
    data = dados["data"]
    hora_inicio = _normalizar_hora(dados["hora_inicio"])
    hora_fim = _validar_horario(data, hora_inicio)

    # Primeiro confere na lista, para devolver a mensagem certa. O índice único
    # do banco continua sendo a garantia final contra duas gravações ao mesmo
    # tempo.
    ocupados = repositorio_agendamentos.listar_ativos_do_tatuador(
        tatuador_id,
        data,
    )

    if any(agendamento["hora_inicio"] == hora_inicio for agendamento in ocupados):
        raise HorarioIndisponivel(
            "O tatuador já tem um agendamento nesse horário."
        )

    return repositorio_agendamentos.criar_agendamento(
        tatuagem_id,
        {
            "tatuador_id": tatuador_id,
            "tipo": tipo,
            "data": data,
            "hora_inicio": hora_inicio,
            "hora_fim": hora_fim,
        },
    )


def cancelar_agendamento(
    tatuagem_id: int,
    agendamento_id: int,
    tatuagem: dict | None,
    usuario: dict,
) -> dict | None:
    """Cancela um agendamento ativo e libera o horário na agenda."""
    if tatuagem is None:
        return None

    agendamento = repositorio_agendamentos.buscar_agendamento(
        tatuagem_id,
        agendamento_id,
    )

    if agendamento is None:
        raise AgendamentoNaoEncontrado(
            "Esse agendamento não existe nesta tatuagem."
        )

    if agendamento["status"] != "agendado":
        raise AgendamentoJaCancelado("Esse agendamento já está cancelado.")

    if (
        usuario["papel"] == "tatuador"
        and usuario["id"] != agendamento["tatuador_id"]
    ):
        raise AgendamentoDeOutroTatuador(
            "Esse agendamento pertence à agenda de outro tatuador."
        )

    cancelado = repositorio_agendamentos.cancelar_agendamento(
        tatuagem_id,
        agendamento_id,
    )

    # Se outra chamada cancelou entre a leitura e a gravação, o UPDATE não
    # encontra mais o status 'agendado' e devolve None.
    if cancelado is None:
        raise AgendamentoJaCancelado("Esse agendamento já está cancelado.")

    return cancelado
