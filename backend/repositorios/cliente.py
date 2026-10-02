"""O depósito das clientes do estúdio.

A cartilha lista três entidades: o usuário, a tatuagem e o passo. O usuário é quem
entra no sistema, e tem um tipo: cliente ou tatuador. A Bruna é a cliente 1, que é
o perfil que existe na tela, e a cliente 2 é outra cliente do mesmo estúdio, que
entra pelo mesmo formulário e aparece na agenda do Vitor.

Este arquivo é só o depósito das clientes, e ele existe por um motivo só: a agenda
do Vitor precisa mostrar de quem é cada tatuagem, e o nome é dado do negócio, não
dado de tela. Guardar o nome aqui, e não dentro de cada tatuagem, evita o mesmo
nome estar escrito em dois lugares e divergir quando alguém corrigir uma das
duas.

Por que este arquivo não tem rota: a cartilha não pede rota de cliente. Ela pede
cinco capacidades, e nenhuma delas é "listar clientes". O que ela pede é que a
agenda mostre a cliente, e o nome indo junto da tatuagem resolve isso sem
inventar rota nenhuma.
"""

# A lista começa no nível do módulo, pelo mesmo motivo da lista de tatuagens: todas
# as funções deste arquivo leem sempre a mesma lista, e ela morre com o processo.
clientes: list[dict] = []


def buscar_cliente(cliente_id: int) -> dict | None:
    """Devolve a cliente de um id, ou None se esse id não existir.

    Devolve None em vez de levantar exceção porque quem decide o que fazer com a
    falta de uma cliente é o serviço, e não este arquivo.
    """
    for cliente in clientes:
        if cliente["id"] == cliente_id:
            return cliente.copy()

    return None


# Dados de demonstração. A Bruna entra como cliente 1 porque é o id que a tela dela
# usa, e porque o id da próxima tatuagem é o tamanho da lista mais um. A segunda
# cliente existe para a agenda do Vitor ter mais de uma linha para mostrar a coluna
# da cliente: com uma só, a coluna não provaria nada.
clientes_de_exemplo = [
    {
        "id": 1,
        "nome": "Bruna",
    },
    {
        "id": 2,
        "nome": "Camila",
    },
]

# O for abaixo joga cada exemplo na lista real, e é a mesma lista que a função acima
# lê. fica no fim do arquivo pelo mesmo motivo da tatuagem: o conteúdo vem depois
# do código, para ficar claro onde o código para.
for exemplo in clientes_de_exemplo:
    clientes.append(exemplo)
