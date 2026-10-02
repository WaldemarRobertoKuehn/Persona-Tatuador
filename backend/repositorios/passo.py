"""O depósito dos passos, agora na tabela passos do MySQL.

Este arquivo é o depósito dos passos, e trabalha igual ao depósito das tatuagens:
guarda, devolve, e não decide nada. A ordem dos passos, que é a regra da
cartilha, é do serviço, e o status HTTP é da rota.

O que mudou quando os dados foram para o banco

    Antes os passos viviam numa lista de dicionários neste arquivo. Agora a lista
    é a tabela passos, e quem guarda é o MySQL.

    A assinatura das funções não mudou uma vírgula: o serviço recebe a mesma
    lista de dicionários e o mesmo dicionário de antes. Como o DictCursor devolve
    cada linha como dicionário, o tipo que sai daqui é o mesmo que entrava.

A data não precisa de conversão

    A coluna data é do tipo DATE, e o pymysql devolve esse tipo como um date do
    Python, que é exatamente o que o esquema de saída declara. Não há o que
    converter aqui, ao contrário do tamanho da tatuagem, que vem como Decimal.
"""

from datetime import date

import banco


def listar_passos(tatuagem_id: int) -> list[dict]:
    """Devolve os passos de uma tatuagem, na ordem em que foram registrados.

    O filtro é obrigatório aqui, diferente do das tatuagens: o histórico que a
    Bruna lê é o de uma tatuagem só, e a pergunta "quais passos existem" sem
    dono não tem resposta útil.

    O ORDER BY id é obrigatório, e é a parte que mais mudou com a chegada do
    banco. Na versão em memória a ordem não precisava ser pedida porque cada passo
    era jogado no fim da lista, e a posição na lista era a ordem em que as coisas
    aconteceram. O MySQL não garante nada disso: ele devolve as linhas na ordem
    que for mais barata para ele, e essa ordem pode mudar de um SELECT para o
    outro. Sem o ORDER BY, o histórico da tatuagem apareceria embaralhado.

    Ordenar pelo id e não pela data é proposital. A ordem em que o passo foi
    registrado e a ordem da data não são sempre a mesma coisa: se o Vitor
    registrar hoje o passo de uma sessão de ontem, a data vai estar fora de
    ordem, e o histórico que ele lê é o que ele registrou, na ordem em que
    registrou.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, tatuagem_id, tipo, data, observacao "
            "FROM passos WHERE tatuagem_id = %s ORDER BY id",
            (tatuagem_id,),
        )

        return cursor.fetchall()


def criar_passo(tatuagem_id: int, dados: dict) -> dict:
    """Grava um passo numa tatuagem e devolve como ele ficou gravado.

    O id não é escrito no INSERT: a coluna é AUTO_INCREMENT, e quem escolhe o
    número é o MySQL. Depois do INSERT, o cursor.lastrowid devolve o número
    gerado, e é com ele que a função busca a linha de novo, pelo mesmo motivo da
    tatuagem: o que volta é o que está gravado.

    A tatuagem dona do passo entra pela função, e não pelo dicionário de dados,
    porque quem diz de que tatuagem é o passo é o caminho da rota, e a rota já
    recebeu esse valor. Assim o mesmo pedido não pode mandar dois donos.

    A data é a de hoje, montada aqui com date.today(). A ficha do Vitor não tem
    campo de data, então a data é do servidor. Ela é entregue ao MySQL como um
    date do Python, e o MySQL guarda no tipo DATE, sem horário. Na volta ela
    continua um date, e por isso o esquema de saída não precisa de nada.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO passos (tatuagem_id, tipo, data, observacao) "
            "VALUES (%s, %s, %s, %s)",
            (
                tatuagem_id,
                dados["tipo"],
                date.today(),
                dados["observacao"],
            ),
        )

        novo_id = cursor.lastrowid

    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, tatuagem_id, tipo, data, observacao FROM passos WHERE id = %s",
            (novo_id,),
        )

        return cursor.fetchone()
