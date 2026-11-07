"""Depósito das imagens de tatuagem.

As listagens nunca pedem a coluna conteudo: o arquivo só é lido quando a rota de
download é chamada. Assim uma tatuagem com várias imagens não arrasta megabytes
para dentro de uma resposta JSON.
"""

import banco


# A lista de colunas fica em um lugar só para não repetir o mesmo SELECT em todas
# as funções. O conteúdo binário fica de fora de propósito.
_COLUNAS = (
    "id, tatuagem_id, nome, content_type, tamanho_bytes, tipo, status, "
    "criado_em, aprovada_em, recusada_em, motivo_recusa"
)


def listar_imagens(tatuagem_id: int) -> list[dict]:
    """Devolve os metadados das imagens de uma tatuagem, em ordem de envio."""
    with banco.cursor() as cursor:
        cursor.execute(
            f"SELECT {_COLUNAS} FROM tatuagem_imagens "
            "WHERE tatuagem_id = %s ORDER BY id",
            (tatuagem_id,),
        )
        return cursor.fetchall()


def buscar_imagem(tatuagem_id: int, imagem_id: int) -> dict | None:
    """Devolve os metadados de uma imagem, ou None se ela não for da tatuagem."""
    with banco.cursor() as cursor:
        cursor.execute(
            f"SELECT {_COLUNAS} FROM tatuagem_imagens "
            "WHERE tatuagem_id = %s AND id = %s",
            (tatuagem_id, imagem_id),
        )
        return cursor.fetchone()


def buscar_conteudo(tatuagem_id: int, imagem_id: int) -> dict | None:
    """Devolve nome, tipo de mídia e bytes da imagem, ou None se não existir."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT nome, content_type, conteudo FROM tatuagem_imagens "
            "WHERE tatuagem_id = %s AND id = %s",
            (tatuagem_id, imagem_id),
        )
        return cursor.fetchone()


def criar_imagem(tatuagem_id: int, dados: dict) -> dict:
    """Grava uma imagem e devolve os metadados dela sem o conteúdo."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tatuagem_imagens "
            "(tatuagem_id, nome, content_type, tamanho_bytes, tipo, conteudo) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            f"RETURNING {_COLUNAS}",
            (
                tatuagem_id,
                dados["nome"],
                dados["content_type"],
                dados["tamanho_bytes"],
                dados["tipo"],
                dados["conteudo"],
            ),
        )
        return cursor.fetchone()


def aprovar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    usuario_id: int,
    aprovada_em,
) -> dict | None:
    """Marca a imagem como aprovada e devolve os metadados atualizados."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE tatuagem_imagens "
            "SET status = 'aprovada', aprovada_em = %s, "
            "aprovada_por_usuario_id = %s, recusada_em = NULL, "
            "motivo_recusa = NULL "
            "WHERE tatuagem_id = %s AND id = %s "
            f"RETURNING {_COLUNAS}",
            (aprovada_em, usuario_id, tatuagem_id, imagem_id),
        )
        return cursor.fetchone()


def recusar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    motivo: str,
    recusada_em,
) -> dict | None:
    """Marca a imagem como recusada, guarda o motivo e limpa a aprovação."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE tatuagem_imagens "
            "SET status = 'recusada', recusada_em = %s, motivo_recusa = %s, "
            "aprovada_em = NULL, aprovada_por_usuario_id = NULL "
            "WHERE tatuagem_id = %s AND id = %s "
            f"RETURNING {_COLUNAS}",
            (recusada_em, motivo, tatuagem_id, imagem_id),
        )
        return cursor.fetchone()


def remover_imagem(tatuagem_id: int, imagem_id: int) -> bool:
    """Apaga a imagem e devolve True quando ela existia na tatuagem."""
    with banco.cursor() as cursor:
        cursor.execute(
            "DELETE FROM tatuagem_imagens "
            "WHERE tatuagem_id = %s AND id = %s RETURNING id",
            (tatuagem_id, imagem_id),
        )
        return cursor.fetchone() is not None
