"""O depósito das tatuagens, agora na tabela tatuagens do MySQL.

Este arquivo é o depósito. Ele guarda os dados e devolve, e nada mais: não sabe
por que um passo é recusado, não escolhe etapa, não monta resposta de erro. A
regra da cartilha vive no serviço, e o status HTTP vive na rota.

O que mudou quando os dados foram para o banco

    Antes os dados viviam numa lista de dicionários dentro deste arquivo, e as
    funções filtravam a lista com list comprehension. Agora a lista é a tabela
    tatuagens, e quem filtra é o MySQL, com a cláusula WHERE.

    A assinatura das funções não mudou uma vírgula, e é isso que interessa: o
    serviço recebe exatamente o mesmo tipo de coisa, uma lista de dicionários ou
    None. Como o DictCursor devolve cada linha como dicionário, o tipo que a
    função entrega é o mesmo de antes, e por isso nenhum esquema, serviço ou rota
    precisou ser tocado.

O que o banco resolve sozinho, e o que ele exige

    O id não é mais calculado com len(tatuagens) + 1. Quem escolhe o número agora
    é a coluna AUTO_INCREMENT da tabela, e o Python pergunta o número gerado com
    cursor.lastrowid. Isso não é só mais bonito: o len() + 1 quebrava assim que
    existisse um DELETE, porque o tamanho da lista deixaria de ser o último id.
    O AUTO_INCREMENT nunca repete número, mesmo com apagados no meio.
"""

import banco


# O tamanho sai do MySQL como Decimal, e não como float, porque a coluna é
# DECIMAL(6,2). Decimal é número exato: 12.50 volta como 12.50, e não como
# 12.499999, que é o defeito clássico do float em medida. O esquema de saída
# declara float, e o Pydantic converteria sozinho, mas converter aqui deixa o
# depósito entregando já no tipo que a tela espera, e evita depender disso.
def _com_tamanho_em_float(tatuagem: dict) -> dict:
    """Devolve a tatuagem com o tamanho convertido de Decimal para float.

    O float() é chamado sobre o valor e não sobre o dicionário inteiro, porque o
    que precisa mudar de tipo é o número do tamanho, e não a linha.
    """
    return {**tatuagem, "tamanho": float(tatuagem["tamanho"])}


def listar_tatuagens(
    etapa: str | None = None, cliente_id: int | None = None
) -> list[dict]:
    """Devolve as tatuagens, filtradas quando o filtro vier preenchido.

    Os dois filtros são opcionais, e é isso que permite a mesma função servir à
    agenda do Vitor, que quer todas as de uma etapa, e à tela da Bruna, que quer
    só as dela. Sem nenhum filtro, devolve a lista inteira.

    A montagem do WHERE é feita em duas listas: uma com as condições e outra com
    os valores, na mesma ordem. Cada filtro que vem preenchido acrescenta uma
    condição e o seu valor. No fim, o AND junta as condições, e os valores vão
    para o execute, que é quem os encaixa nos %s na ordem.

    Montar o texto com a condição condicional assim, e não escrever um WHERE
    pronto, é o que permite a mesma consulta servir aos dois casos: sem filtro o
    WHERE nem entra na consulta, e com os dois filtros ele vira "WHERE etapa = %s
    AND cliente_id = %s". A alternativa era escrever quatro consultas inteiras,
    uma para cada combinação de filtro, e o mesmo dado quatro vezes no arquivo.
    """
    condicoes = []
    valores = []

    if etapa is not None:
        condicoes.append("etapa = %s")
        valores.append(etapa)

    if cliente_id is not None:
        condicoes.append("cliente_id = %s")
        valores.append(cliente_id)

    sql = (
        "SELECT id, cliente_id, ideia, local_do_corpo, tamanho, etapa "
        "FROM tatuagens"
    )

    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)

    with banco.cursor() as cursor:
        cursor.execute(sql, valores)

        achadas = cursor.fetchall()

    return [_com_tamanho_em_float(tatuagem) for tatuagem in achadas]


def buscar_tatuagem(tatuagem_id: int) -> dict | None:
    """Devolve a tatuagem de um id, ou None se esse id não existir.

    Devolve None em vez de levantar exceção porque quem decide o que responder
    com 404 é a rota, e não este arquivo.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, cliente_id, ideia, local_do_corpo, tamanho, etapa "
            "FROM tatuagens WHERE id = %s",
            (tatuagem_id,),
        )

        achada = cursor.fetchone()

    if achada is None:
        return None

    return _com_tamanho_em_float(achada)


def criar_tatuagem(dados: dict) -> dict:
    """Grava uma tatuagem nova e devolve como ela ficou gravada.

    O id não é escrito no INSERT. A coluna é AUTO_INCREMENT, e quem escolhe o
    número é o MySQL, sem o Python saber o último id gravado. Depois do INSERT, o
    cursor.lastrowid devolve o número que o MySQL escolheu, e é com ele que a
    função busca a linha de novo.

    Voltar a buscar em vez de devolver o dicionário montado tem uma vantagem que
    vale a pena: o que volta da consulta é o que está gravado no banco, e não o
    que o Python acha que gravou. Se o MySQL tiver convertido alguma coisa, o que
    a tela recebe é a versão convertida.

    A etapa chega pronta em dados, e não é este arquivo que decide qual é. Quem
    decide é o serviço, porque "a tatuagem nova começa pedida" é a regra da
    cartilha, e regra não mora no depósito. Aqui só se copia o que veio.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tatuagens "
            "(cliente_id, ideia, local_do_corpo, tamanho, etapa) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                dados["cliente_id"],
                dados["ideia"],
                dados["local_do_corpo"],
                dados["tamanho"],
                dados["etapa"],
            ),
        )

        novo_id = cursor.lastrowid

    return buscar_tatuagem(novo_id)


def atualizar_etapa(tatuagem_id: int, etapa: str) -> dict | None:
    """Grava a etapa nova de uma tatuagem e devolve como ela ficou.

    Esta função existe para o serviço, que é quem sabe qual é a etapa que aquele
    passo aceita. Ela não decide a etapa: recebe. E devolve None se a tatuagem
    não existir, para a rota tratar do 404.

    Por que a função não confere a existência pelo rowcount, que é o número de
    linhas que o UPDATE mexeu

    Porque esse número mente justamente no caso que este projeto usa. Registrar
    uma segunda sessão numa tatuagem que já está "em sessões" faz a etapa ir para
    "em sessões" outra vez, ou seja, o valor não muda. O MySQL conta isso como zero
    linhas alteradas, igual a uma tatuagem que não existe, e o serviço passaria a
    receber None e a rota a responder 404 onde devia responder 201. Por isso a
    função grava e depois pergunta, e é a busca que decide se a tatuagem existe.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE tatuagens SET etapa = %s WHERE id = %s",
            (etapa, tatuagem_id),
        )

    return buscar_tatuagem(tatuagem_id)
