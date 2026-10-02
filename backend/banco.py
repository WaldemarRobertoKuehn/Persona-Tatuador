"""A porta de entrada no MySQL, compartilhada pelos três repositórios.

Este arquivo é a única parte do back que sabe que existe um banco de dados. Os
três repositórios pedem um cursor a ele e recebem um cursor pronto, e nunca
mencionam driver, conexão nem senha. Se um dia o banco mudar, é só este arquivo
que muda.

Por que este arquivo existe, sendo que a regra do projeto lista os arquivos do
backend e este não estava na lista

    A regra manda configuracao.py ser o único arquivo que lê o .env, e ela cumpre
    isso: os dados de conexão saem de lá, e não daqui. O que este arquivo faz é
    o passo seguinte, que é abrir a conexão de verdade. Guardar esse passo em
    qualquer um dos três repositórios significaria o mesmo código repetido três
    vezes, e o dia que a senha mudasse de lugar seriam três lugares para mudar.
    Um arquivo só, com o nome do que ele é, é mais honesto do que um pedaço
    desse passo escondido dentro de um repositório.

O que é o pymysql

    O pymysql é o driver: é a biblioteca que traduz o SQL do Python para o
    protocolo de rede do MySQL. Sem ele não existe como falar com o servidor a
    partir do Python, do mesmo jeito que não existe como falar HTTP sem a
    biblioteca de requests. Ele não é ORM: não escreve SQL por nós, não inventa
    classe, não esconde a consulta. É só o canal, e por isso o SQL deste projeto
    fica visível, escrito à mão, o que é bem mais fácil de defender na
    apresentação do que uma classe que ninguém sabe explicar.

O que é o with

    O with é uma forma de garantir que um recurso seja fechado, mesmo se algo no
    meio der erro. O que está indentado dentro do with é o que usa o cursor; ao
    sair do bloco, por qualquer motivo, o commit e o fechamento acontecem. Sem o
    with, cada função teria que fechar a conexão à mão, e uma função que
    esquecesse deixaria conexão vazada no servidor.

Arazão de ser do commit

    O MySQL não grava nada até receber um commit. O commit é o "agora pode
    guardar" dele. Sem ele, um SELECT devolve a linha, mas um INSERT se perde
    quando o processo morre. Por isso o commit está aqui, num lugar só, e não
    espalhado por função: o banco decide quando fecha a transação, e não cada
    repositório.
"""

# contextmanager é do Python, não do pymysql: é o que permite transformar uma
# função comum num gerenciador de contexto, que é o que o with consegue usar.
from contextlib import contextmanager

import pymysql

# DictCursor é um cursor que devolve cada linha como dicionário, e não como
# tupla. Ele importa porque é exatamente o formato que os repositórios já
# devolviam: um dicionário com as colunas da tabela. A troca das listas em
# memória pelo banco não muda nenhum tipo de dado, e por isso nenhum esquema, nem
# serviço, nem rota precisou ser tocado.
from pymysql.cursors import DictCursor

# Import de módulo com `import configuracao`: este arquivo não puxa nenhuma
# função solta da configuração, segue a mesma convenção do main.py.
import configuracao


@contextmanager
def cursor() -> DictCursor:
    """Abre a conexão, entrega um cursor e garante o commit e o fechamento.

    O nome é cursor e não conexao porque é o cursor que os repositórios usam de
    verdade: o cursor é quem executa a consulta e traz a linha de volta.

    A partir de agora, tudo que este arquivo faz cabe em três passos, e os
    três precisam acontecer: conectar, entregar o cursor, e depois gravar e
    fechar. O try/finally existe para o passo dois nunca pular o passo três: se
    o repositório quebrar no meio de uma consulta, a conexão é fechada assim
    mesmo, e o servidor não fica acumulando conexão morta.
    """
    # Os cinco valores de conexão vêm prontos do configuracao.py, que é quem leu
    # o .env. Eles são repassados um a um, com o nome que o pymysql exige, porque
    # o pymysql é uma biblioteca de fora e fala o nome dos argumentos em inglês.
    # O nome da variável continua em português: só o argumento da biblioteca é
    # inglês. Passar por extenso também é mais legível do que o **, que exigiria
    # que a chave do dicionário tivesse exatamente o nome do argumento.
    dados = configuracao.endereco_do_banco()

    conexao = pymysql.connect(
        host=dados["host"],
        port=dados["porta"],
        user=dados["usuario"],
        password=dados["senha"],
        database=dados["banco"],
        cursorclass=DictCursor,
        # O charset precisa ser utf8mb4 pelo mesmo motivo do esquema.sql: a tabela
        # guarda "sessão" e "não desista", e sem utf8mb4 esses acentos voltariam
        # cortados ou com interrogação no lugar.
        charset="utf8mb4",
        # autocommit=False é o padrão do pymysql, e está escrito para ficar claro
        # que quem manda gravar é o commit do fim desta função, e não cada
        # consulta. É esse controle que permite gravar a tatuagem e a etapa dela
        # juntas, ou nenhuma das duas.
        autocommit=False,
    )

    try:
        with conexao.cursor() as cursor_do_banco:
            yield cursor_do_banco

        # O commit fica depois do with interno e ainda dentro do try: ele só roda
        # se o repositório terminou sem erro. Se deu erro no meio, o commit é
        # pulado e nada é gravado, que é o comportamento correto.
        conexao.commit()
    finally:
        # O finally roda sempre, com ou sem erro. Fechar a conexão aqui é o que
        # impede o acúmulo de conexões abertas no servidor.
        conexao.close()
