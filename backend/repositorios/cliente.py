"""O depósito das clientes do estúdio, agora no MySQL.

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

# A lista de clientes some daqui: no banco ela é a tabela clientes do esquema.sql.
# Este import é o mesmo que o main.py faz, por módulo e com `as`, e o apelido deixa
# claro que o que está do outro lado é o banco, e não uma lista na memória.
import banco


def buscar_por_email(email: str) -> dict | None:
    """Busca uma conta pelo email, sem devolver dados além dos necessários."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE email = %s",
            (email,),
        )
        return cursor.fetchone()


def criar_usuario(nome: str, email: str, senha_hash: str) -> dict:
    """Cria a conta e devolve seus dados públicos e o hash para uso interno."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO clientes (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash),
        )
        usuario_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """Busca conta por id, incluindo o hash somente para validação interna."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def buscar_cliente(cliente_id: int) -> dict | None:
    """Devolve a cliente de um id, ou None se esse id não existir.

    O SELECT pede as duas colunas pelo nome, e não usa o asterisco. O asterisco
    traria qualquer coluna que alguém acrescentasse na tabela depois, e o
    dicionário devolvido passaria a ter uma chave a mais sem ninguém pedir.

    O WHERE usa o %s, e nunca uma f-string com o número escrito dentro. Esse %s é
    um espaço reservado: o pymysql troca ele pelo valor do segundo argumento,
    com escape, e o valor chega ao MySQL como texto, nunca como parte do comando.
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
