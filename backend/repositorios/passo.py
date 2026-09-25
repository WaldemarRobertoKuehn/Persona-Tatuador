"""A lista de passos em memória e as funções que leem e gravam nela.

Este arquivo é o depósito dos passos, e trabalha igual ao depósito das tatuagens:
guarda, devolve, e não decide nada. A ordem dos passos, que é a regra da
cartilha, é do serviço, e o status HTTP é da rota.

A lista vive dentro do arquivo, sem banco, conforme a regra do projeto. Quando o
back reinicia, ela volta vazia.

Cada passo é um dicionário com as mesmas chaves do esquema de saída: id,
tatuagem_id, tipo, data e observacao.
"""

from datetime import date

# A lista de passos é separada da lista de tatuagens, porque cada arquivo guarda o
# seu próprio depósito. Os dois ficam no nível do módulo, para sobreviverem à
# passagem de uma função para outra.
passos: list[dict] = []


def listar_passos(tatuagem_id: int) -> list[dict]:
    """Devolve os passos de uma tatuagem, na ordem em que foram registrados.

    O filtro é obrigatório aqui, diferente do das tatuagens: o histórico que a
    Bruna lê é o de uma tatuagem só, e a pergunta "quais passos existem" sem
    dono não tem resposta útil.

    A lista não é ordenada com sorted. Ordenar não entra neste projeto, e não
    precisa: como nada apaga passo, cada passo entra no fim da lista quando é
    gravado, então a ordem da lista já é a ordem em que as coisas aconteceram.
    """
    return [passo for passo in passos if passo["tatuagem_id"] == tatuagem_id]


def criar_passo(tatuagem_id: int, dados: dict) -> dict:
    """Grava um passo numa tatuagem e devolve como ele ficou gravado.

    O id é montado com o tamanho da lista mais um, pelo mesmo motivo do depósito
    de tatuagens: o id é do depósito, e o front não escolhe id. Como nada apaga
    passo nesta API, o número não se repete.

    A tatuagem dona do passo entra pela função, e não pelo dicionário de dados,
    porque quem diz de que tatuagem é o passo é o caminho da rota, e a rota já
    recebeu esse valor. Assim o mesmo pedido não pode mandar dois donos.

    A data é a de hoje, montada aqui com date.today(). A ficha do Vitor não tem
    campo de data, então a data é do servidor. Ela fica guardada como date, que é
    o tipo que o MySQL vai devolver no ciclo 2.
    """
    passo = {
        "id": len(passos) + 1,
        "tatuagem_id": tatuagem_id,
        "tipo": dados["tipo"],
        "data": date.today(),
        "observacao": dados["observacao"],
    }

    passos.append(passo)

    return passo.copy()


# Dados de demonstração, com a mesma finalidade dos da tatuagem: conteúdo para a
# apresentação, não regra. Cada histórico é compatível com a etapa em que a
# tatuagem está, senão a demonstração mostraria uma coisa que a regra proíbe.
#
# A tatuagem 4 é a única sem passo nenhum, porque ela está em "pedida": é o
# exemplo vivo da regra de que nada acontece antes do desenho aprovado. O id vai
# de 1 a 10 sem buraco, para o próximo passo criado na apresentação sair com o 11.
passos_de_exemplo = [
    {
        "id": 1,
        "tatuagem_id": 1,
        "tipo": "desenho aprovado",
        "data": date(2026, 8, 3),
        "observacao": "a cliente aprovou o desenho, sem ajuste",
    },
    {
        "id": 2,
        "tatuagem_id": 1,
        "tipo": "sessão",
        "data": date(2026, 8, 10),
        "observacao": "contorno com linha fina, sem preenchimento",
    },
    {
        "id": 3,
        "tatuagem_id": 1,
        "tipo": "sessão",
        "data": date(2026, 8, 17),
        "observacao": "preenchimento do fundo e ajuste de traço",
    },
    {
        "id": 4,
        "tatuagem_id": 1,
        "tipo": "retoque",
        "data": date(2026, 9, 14),
        "observacao": "retoque na ponta de um pétala",
    },
    {
        "id": 5,
        "tatuagem_id": 2,
        "tipo": "desenho aprovado",
        "data": date(2026, 9, 1),
        "observacao": "aprovado depois de duas mudanças no desenho",
    },
    {
        "id": 6,
        "tatuagem_id": 2,
        "tipo": "sessão",
        "data": date(2026, 9, 8),
        "observacao": "primeira sessão, só a linha",
    },
    {
        "id": 7,
        "tatuagem_id": 3,
        "tipo": "desenho aprovado",
        "data": date(2026, 9, 15),
        "observacao": "desenho aprovado, a tattoo entra na fila das sessões",
    },
    {
        "id": 8,
        "tatuagem_id": 5,
        "tipo": "desenho aprovado",
        "data": date(2026, 9, 5),
        "observacao": "texto na fonte escolhida pela cliente",
    },
    {
        "id": 9,
        "tatuagem_id": 5,
        "tipo": "sessão",
        "data": date(2026, 9, 12),
        "observacao": "rascunho da letra",
    },
    {
        "id": 10,
        "tatuagem_id": 5,
        "tipo": "sessão",
        "data": date(2026, 9, 19),
        "observacao": "letra fechada, aguardando a cicatrização para o retoque",
    },
]

# O for abaixo joga cada exemplo na lista real, a mesma que criar_passo usa.
for exemplo in passos_de_exemplo:
    passos.append(exemplo)
