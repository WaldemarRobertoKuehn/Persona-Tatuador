"""Depósito dos agendamentos de sessão e retoque.

O nome do tatuador entra junto na consulta porque a tela precisa exibir quem é o
responsável pelo horário, e a tabela de agendamentos guarda só o id. A agenda é
sempre filtrada por tatuador: dois tatuadores podem atender no mesmo horário.
"""

import banco


# As colunas do agendamento mais o nome do tatuador. O alias u evita conflito
# com a tabela de tatuagens.
_COLUNAS = (
    "a.id, a.tatuagem_id, a.tatuador_id, u.nome AS tatuador_nome, a.tipo, "
    "a.data, a.hora_inicio, a.hora_fim, a.status, a.criado_em"
)


def _selecionar() -> str:
    """Monta o SELECT base com o JOIN no tatuador."""
    return (
        f"SELECT {_COLUNAS} FROM agendamentos a "
        "JOIN usuarios u ON u.id = a.tatuador_id "
    )


def listar_agendamentos(tatuagem_id: int) -> list[dict]:
    """Devolve os agendamentos de uma tatuagem, dos mais antigos aos novos."""
    with banco.cursor() as cursor:
        cursor.execute(
            _selecionar()
            + "WHERE a.tatuagem_id = %s ORDER BY a.data, a.hora_inicio",
            (tatuagem_id,),
        )
        return cursor.fetchall()


def buscar_agendamento(tatuagem_id: int, agendamento_id: int) -> dict | None:
    """Devolve um agendamento da tatuagem, ou None se não existir."""
    with banco.cursor() as cursor:
        cursor.execute(
            _selecionar()
            + "WHERE a.tatuagem_id = %s AND a.id = %s",
            (tatuagem_id, agendamento_id),
        )
        return cursor.fetchone()


def criar_agendamento(tatuagem_id: int, dados: dict) -> dict:
    """Grava um agendamento e devolve os dados já com o nome do tatuador."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO agendamentos "
            "(tatuagem_id, tatuador_id, tipo, data, hora_inicio, hora_fim) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (
                tatuagem_id,
                dados["tatuador_id"],
                dados["tipo"],
                dados["data"],
                dados["hora_inicio"],
                dados["hora_fim"],
            ),
        )
        agendamento_id = cursor.fetchone()["id"]

        # A leitura logo depois traz o nome do tatuador que a tela usa; o INSERT
        # sozinho não consegue juntar a tabela usuarios no RETURNING.
        cursor.execute(
            _selecionar()
            + "WHERE a.tatuagem_id = %s AND a.id = %s",
            (tatuagem_id, agendamento_id),
        )
        return cursor.fetchone()


def cancelar_agendamento(tatuagem_id: int, agendamento_id: int) -> dict | None:
    """Marca o agendamento como cancelado, se ele ainda estiver ativo."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE agendamentos SET status = 'cancelado' "
            "WHERE tatuagem_id = %s AND id = %s AND status = 'agendado' "
            "RETURNING id",
            (tatuagem_id, agendamento_id),
        )

        if cursor.fetchone() is None:
            return None

        cursor.execute(
            _selecionar()
            + "WHERE a.tatuagem_id = %s AND a.id = %s",
            (tatuagem_id, agendamento_id),
        )
        return cursor.fetchone()


def listar_ativos_do_tatuador(tatuador_id: int, data) -> list[dict]:
    """Devolve os agendamentos ativos de um tatuador num dia.

    A lista serve tanto para marcar os horários ocupados na disponibilidade
    quanto para conferir o conflito antes de gravar. A regra de expediente não
    mora aqui: o depósito só devolve o que está no banco.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, hora_inicio, hora_fim FROM agendamentos "
            "WHERE tatuador_id = %s AND data = %s AND status = 'agendado' "
            "ORDER BY hora_inicio",
            (tatuador_id, data),
        )
        return cursor.fetchall()
