"""Cria as contas de demonstração, na tabela usuarios.

Uma vez por banco de estudo: roda com `python criar_contas_de_demonstracao.py`,
de dentro de backend/. Ele deixa o sistema pronto para a apresentação, com as
duas contas que a cartilha pede e a conta do dono do estúdio.

As três contas

    Bruna   papel cliente, ligada à cliente 1 da tabela clientes. É a conta que
            vê "pedir tatuagem" e "minhas tatuagens", e ela enxerga as cinco
            tatuagens que a Bruna tem.
    Vitor   papel tatuador. É a conta que vê "a agenda" e "a ficha".
    Waldemar  papel tatuador, a conta do dono do estúdio. A senha desta conta
            não muda: o hash que já estava na tabela clientes é copiado para a
            tabela usuarios, e as colunas velhas são esvaziadas.

Por que as contas são criadas por este arquivo e não pela tela

    A tela de login do front não tem cadastro: quem entra já tem conta. E o
    papel "tatuador" não vem da tela, porque quem decide isso é o estúdio, e
    não quem se cadastrou. Por isso a criação das contas é uma tarefa de
    montagem do banco, feita pelo serviço, e não uma rota pública.

O que o arquivo usa

    Só a camada de serviço: cadastrar e mover_conta. O serviço chama o
    repositório, o repositório chama o banco, e o arquivo só conta o que
    aconteceu. Nenhum SQL é escrito aqui.

Repetir o comando

    O script é idempotente: uma conta que já existe é pulada, e a mensagem
    diz qual é. Rodar de novo não quebra nada e não cria conta duplicada.
"""

# O serviço, que é a camada das decisões: quem entra, com que papel e de que
# jeito a senha é guardada.
import servicos.usuario as servico_usuarios

# O repositório de clientes, só para achar a Bruna pelo nome: a conta dela é
# ligada à linha da Bruna na tabela clientes, e não a uma linha nova.
import repositorios.cliente as repositorio_clientes


# As contas de demonstração. A senha de cada uma é conhecida de propósito: este
# é um banco de estudo, e a conta precisa ser acessível na hora da apresentação.
CONTAS_DE_DEMONSTRACAO = [
    {
        "nome": "Bruna",
        "email": "bruna@tracofino.com.br",
        "senha": "bruna123",
        "papel": "cliente",
    },
    {
        "nome": "Vitor",
        "email": "vitor@tracofino.com.br",
        "senha": "vitor123",
        "papel": "tatuador",
    },
]


def criar_conta_de_demonstracao(conta: dict) -> None:
    """Cria uma conta de cliente ou de tatuador e conta o que aconteceu."""
    # A conta de cliente é ligada a uma cliente que já existe. Quando o nome
    # não está na tabela clientes, a pessoa ainda não é cliente do estúdio e a
    # linha dela é criada pelo serviço, junto com a conta.
    cliente = repositorio_clientes.buscar_cliente_por_nome(conta["nome"])

    dados = {
        "nome": conta["nome"],
        "email": conta["email"],
        "senha": conta["senha"],
        "papel": conta["papel"],
        "cliente_id": cliente["id"] if cliente else None,
    }

    usuario = servico_usuarios.cadastrar(dados)

    if usuario is None:
        print(f"- {conta['nome']}: conta ja existia, pulada.")
        return

    print(
        f"- {usuario['nome']}: id {usuario['id']}, papel {usuario['papel']}, "
        f"cliente_id {usuario['cliente_id']}."
    )


def mover_conta_do_dono() -> None:
    """Leva a conta do dono do estúdio da tabela clientes para a tabela usuarios."""
    # A conta do dono é a linha de clientes que ainda tem email e senha_hash, e
    # é o próprio banco que diz qual é: o email preenchido é a pista.
    acesso = repositorio_clientes.buscar_conta_antiga()

    if acesso is None or not acesso.get("email"):
        print("- Waldemar: nao ha conta antiga para mover.")
        return

    conta = servico_usuarios.mover_conta(acesso["id"], "tatuador")

    if conta is None:
        print("- Waldemar: conta ja existia na tabela usuarios, pulada.")
        return

    print(
        f"- {conta['nome']}: id {conta['id']}, papel {conta['papel']}, "
        "senha mantida."
    )


print("Contas de demonstracao:")
for conta in CONTAS_DE_DEMONSTRACAO:
    criar_conta_de_demonstracao(conta)
mover_conta_do_dono()

print("Entrar com:")
print("  Bruna    bruna@tracofino.com.br  bruna123  (cliente)")
print("  Vitor    vitor@tracofino.com.br  vitor123  (tatuador)")
print("  Waldemar waldemarroberto.kuehn@gmail.com  (senha de antes)")
