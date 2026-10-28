"""O depósito das clientes do estúdio, agora no PostgreSQL.

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

O que mudou quando os dados foram para o banco

    Antes este arquivo guardava tudo numa lista de dicionários criada no próprio
    módulo, e as funções só caminhavam por ela com for. Agora a lista é a tabela
    clientes, e as funções pedem um cursor ao banco.py.

    A assinatura das funções não mudou uma vírgula, e é isso que interessa: o
    serviço que chama este arquivo continua recebendo exatamente o mesmo tipo de
    coisa, um dicionário ou None. Quem consome o depósito não percebeu a troca,
    e é por isso que nem o serviço nem a rota precisaram ser mexidos.
"""

# A lista de clientes some daqui: no banco ela é a tabela clientes, desenhada no
# modelo de backend/modelos/cliente.py.
# Este import é o mesmo que o main.py faz, por módulo e com `as`, e o apelido deixa
# claro que o que está do outro lado é o banco, e não uma lista na memória.
import banco


def buscar_cliente(cliente_id: int) -> dict | None:
    """Devolve a cliente de um id, ou None se esse id não existir.

    O SELECT pede as duas colunas pelo nome, e não usa o asterisco. O asterisco
    traria qualquer coluna que alguém acrescentasse na tabela depois, e o
    dicionário devolvido passaria a ter uma chave a mais sem ninguém pedir.

    O WHERE usa o %s, e nunca uma f-string com o número escrito dentro. Esse %s é
    um espaço reservado: o psycopg2 troca ele pelo valor do segundo argumento,
    com escape, e o valor chega ao PostgreSQL como texto, nunca como parte do comando.
    É o que impede alguém de mandar um cliente_id que carregue junto um comando
    de SQL, e a proteção vale mesmo quando o valor é só um número.

    O fetchone devolve a primeira linha, ou None se não houver nenhuma. Por isso
    a função já devolve None quando a cliente não existe, e o serviço continua
    decidindo o que fazer com a falta, como decidia antes.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome FROM clientes WHERE id = %s",
            (cliente_id,),
        )

        return cursor.fetchone()


def buscar_cliente_por_nome(nome: str) -> dict | None:
    """Devolve a cliente com esse nome, ou None se ninguém tiver esse nome.

    A comparação é feita com LOWER, porque o nome escrito na tela e o nome que
    está gravado podem ter diferença de maiúscula, e a pessoa é a mesma. Sem
    isso, a mesma cliente entraria duas vezes na tabela, e o nome dela passaria
    a estar escrito em dois lugares.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome FROM clientes WHERE LOWER(nome) = LOWER(%s)",
            (nome,),
        )

        return cursor.fetchone()


def criar_cliente(nome: str) -> int:
    """Cria a cliente e devolve o id que o PostgreSQL escolheu para ela."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO clientes (nome) VALUES (%s) RETURNING id",
            (nome,),
        )
        return cursor.fetchone()["id"]


def buscar_acesso(cliente_id: int) -> dict | None:
    """Devolve o email e o hash de senha que ficaram na tabela clientes.

    Essas duas colunas esvaziaram quando a conta passou a morar na tabela
    usuarios, mas elas continuam no desenho da tabela, porque a regra do
    projeto proíbe apagar coluna. A função existe para a conta que ainda está
    nestas colunas ser levada para a tabela usuarios sem que a senha mude: o
    hash é copiado como está, e a senha que a pessoa já conhece continua
    valendo.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE id = %s",
            (cliente_id,),
        )

        return cursor.fetchone()


def buscar_conta_antiga() -> dict | None:
    """Devolve a linha de clientes que ainda tem conta nestas colunas.

    O email e o hash são a pista: a conta do dono do estúdio foi criada
    quando o login morava na tabela clientes, e é a única linha que ficou com
    as duas colunas preenchidas. O LIMIT 1 é porque só existe uma conta
    antiga, e o primeiro achado é a linha procurada.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes "
            "WHERE email IS NOT NULL AND senha_hash IS NOT NULL LIMIT 1"
        )

        return cursor.fetchone()


def esvaziar_acesso(cliente_id: int) -> None:
    """Esvazia as colunas de acesso da cliente, depois que a conta foi movida.

    Sem esta limpeza, o mesmo email e o mesmo hash ficariam escritos em dois
    lugares, e a divergência apareceria na primeira correção: um dos dois
    lados mudaria, e o outro continuaria com o valor velho.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE clientes SET email = NULL, senha_hash = NULL WHERE id = %s",
            (cliente_id,),
        )
