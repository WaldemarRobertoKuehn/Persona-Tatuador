"""A lista de tatuagens em memória e as funções que leem e gravam nela.

Este arquivo é o depósito. Ele guarda os dados e devolve, e nada mais: não sabe
por que um passo é recusado, não escolhe etapa, não monta resposta de erro. A
regra da cartilha vive no serviço, e o status HTTP vive na rota.

Os dados ficam numa lista de dicionários dentro do próprio arquivo, porque a regra
do projeto é que ainda não há banco: nada de SQL, nada de ORM, nada de migração.
A lista vive enquanto o processo do Python estiver vivo. Quando o back reinicia,
ela volta vazia, e isso é o combinado até os dados irem para o MySQL.

Cada tatuagem é um dicionário com as mesmas chaves do esquema de saída: id,
cliente_id, ideia, local_do_corpo, tamanho e etapa.
"""

# A lista começa vazia, no nível do módulo, para que todas as funções deste
# arquivo leiam e escrevam sempre na mesma lista. Se ela fosse criada dentro de
# cada função, cada chamada veria uma lista nova e os dados sumiriam.
tatuagens: list[dict] = []


def listar_tatuagens(
    etapa: str | None = None, cliente_id: int | None = None
) -> list[dict]:
    """Devolve as tatuagens, filtradas quando o filtro vier preenchido.

    Os dois filtros são opcionais, e é isso que permite a mesma função servir à
    agenda do Vitor, que quer todas as de uma etapa, e à tela da Bruna, que quer
    só as dela. Sem nenhum filtro, devolve a lista inteira.

    A lista devolvida é uma cópia: quem chama pode mexer nela sem estragar o
    depósito. E a lista do depósito não é ordenada, porque ordenar é decisão de
    tela, e a tela é do front.
    """
    achadas = tatuagens

    if etapa is not None:
        achadas = [tatuagem for tatuagem in achadas if tatuagem["etapa"] == etapa]

    if cliente_id is not None:
        achadas = [
            tatuagem for tatuagem in achadas if tatuagem["cliente_id"] == cliente_id
        ]

    return achadas.copy()


def buscar_tatuagem(tatuagem_id: int) -> dict | None:
    """Devolve a tatuagem de um id, ou None se esse id não existir.

    Devolve None em vez de levantar exceção porque quem decide o que responder
    com 404 é a rota, e não este arquivo.
    """
    for tatuagem in tatuagens:
        if tatuagem["id"] == tatuagem_id:
            return tatuagem.copy()

    return None


def criar_tatuagem(dados: dict) -> dict:
    """Grava uma tatuagem nova e devolve como ela ficou gravada.

    O id é montado aqui, com o tamanho da lista mais um, porque o id é do
    depósito: o front não escolhe id, e o serviço não precisa saber de onde ele
    saiu. Como nada nesta API apaga tatuagem, esse número não se repete.

    A etapa chega pronta em dados, e não é este arquivo que decide qual é. Quem
    decide é o serviço, porque "a tatuagem nova começa pedida" é a regra da
    cartilha, e regra não mora no depósito. Aqui só se copia o que veio.
    """
    tatuagem = {
        "id": len(tatuagens) + 1,
        "cliente_id": dados["cliente_id"],
        "ideia": dados["ideia"],
        "local_do_corpo": dados["local_do_corpo"],
        "tamanho": dados["tamanho"],
        "etapa": dados["etapa"],
    }

    tatuagens.append(tatuagem)

    return tatuagem.copy()


def atualizar_etapa(tatuagem_id: int, etapa: str) -> dict | None:
    """Grava a etapa nova de uma tatuagem e devolve como ela ficou.

    Esta função existe para o serviço, que é quem sabe qual é a etapa que aquele
    passo aceita. Ela não decide a etapa: recebe. E devolve None se a tatuagem
    não existir, para a rota tratar do 404.

    A busca é pelo laço em vez de indexar a lista pela posição, porque a posição
    na lista não é o id: um filtro pode ter devolvido três itens, e o id de cada
    um deles continua valendo.
    """
    for tatuagem in tatuagens:
        if tatuagem["id"] == tatuagem_id:
            tatuagem["etapa"] = etapa
            return tatuagem.copy()

    return None


# Dados de demonstração. Eles não são regra, são conteúdo: existem só para a
# agenda e a tela da cliente nascerem com coisa dentro na hora de apresentar.
# Estão no fim do arquivo de propósito, porque é a última coisa que este arquivo
# faz, e assim fica claro onde o conteúdo para e começa o código.
#
# A lista está montada com as quatro etapas, uma tatuagem em cada, de propósito:
# é assim que o filtro por etapa da agenda tem o que mostrar. O id vai de 1 a 5
# sem buraco, porque o id da próxima tatuagem é o tamanho da lista mais um.
#
# Repare que existem duas clientes, e não uma só. A Bruna é a cliente 1, que é o
# perfil que existe na tela; a cliente 2 é outra cliente do mesmo estúdio, e ela
# entra pelo mesmo formulário. A diferença aparece na agenda do Vitor, que mostra
# as duas, e na tela da Bruna, que mostra só a dela.
tatuagens_de_exemplo = [
    {
        "id": 1,
        "cliente_id": 1,
        "ideia": "ramo de cerejeira no antebraço",
        "local_do_corpo": "antebraço",
        "tamanho": 12.5,
        "etapa": "finalizada",
    },
    {
        "id": 2,
        "cliente_id": 1,
        "ideia": "serpente enrolada na canela",
        "local_do_corpo": "canela",
        "tamanho": 20.0,
        "etapa": "em sessões",
    },
    {
        "id": 3,
        "cliente_id": 2,
        "ideia": "rosa no pulso esquerdo",
        "local_do_corpo": "pulso",
        "tamanho": 7.0,
        "etapa": "desenho aprovado",
    },
    {
        "id": 4,
        "cliente_id": 1,
        "ideia": "casa no porta-retrato da coxa",
        "local_do_corpo": "coxa",
        "tamanho": 15.0,
        "etapa": "pedida",
    },
    {
        "id": 5,
        "cliente_id": 2,
        "ideia": "texto 'não desista' no antebraço",
        "local_do_corpo": "antebraço",
        "tamanho": 9.0,
        "etapa": "em sessões",
    },
]

# O for abaixo joga cada exemplo na lista real. É a mesma lista que as funções
# acima leem e escrevem, e por isso a tattoo que o Vitor registrar na demonstração
# entra logo depois da 5, com o id 6, sem atropelar o exemplo.
for exemplo in tatuagens_de_exemplo:
    tatuagens.append(exemplo)
