"""Leitura do .env.

Este arquivo é o único do projeto que lê variável de ambiente, porque a regra do
projeto é assim: o que muda de máquina para máquina entra no .env, e a leitura dele
fica concentrada aqui. Por isso nenhuma rota, nenhum serviço e nenhum repositório
chama os.getenv: todos pedem o valor a este arquivo.
"""

import os

# load_dotenv() lê o arquivo .env e coloca cada chave dele como variável de ambiente
# do processo. Sem essa chamada, o os.getenv lá embaixo não encontraria nada.
from dotenv import load_dotenv

# URL é a classe do SQLAlchemy que representa o endereço do banco já em partes:
# driver, usuário, senha, host, porta e nome. Montar o endereço com URL.create, em
# vez de escrever o texto na mão, é o que resolve o problema da senha com caractere
# estranho: o SQLAlchemy escapa o valor na hora de montar o texto, e não a gente.
from sqlalchemy.engine import URL

load_dotenv()


def endereco_do_front() -> str:
    """Devolve o endereço exato do meu front, que é o único liberado no CORS.

    O segundo argumento do os.getenv é um valor padrão, usado só se a chave não
    estiver no .env. Ele existe para o back subir mesmo numa máquina sem .env, e não
    muda nada quando o .env existe: quem manda é o valor de lá.
    """
    return os.getenv("ORIGEM_FRONTEND", "http://localhost:5173")


def endereco_do_banco() -> URL:
    """Devolve o endereço do MySQL como URL, montado a partir do .env.

    O endereço é devolvido em partes e não como um texto pronto, e o motivo é a
    senha: o .env é um arquivo texto, e a senha pode ter @, : ou /, que são os
    caracteres que separam as partes do endereço. Escrevendo o endereço inteiro num
    só texto, o SQLAlchemy não teria como saber onde acaba a senha, e a conexão
    falharia. Com URL.create, cada parte entra no seu lugar, com o nome do
    argumento, e quem monta o texto é o SQLAlchemy.

    drivername é o par driver+dialeto, escrito no formato do SQLAlchemy: o
    "mysql+" é o nome do dialeto e o que vem depois é o driver que fala com o
    MySQL, que aqui é o mysql-connector-python. A regra do projeto é esse driver, e
    não o pymysql.

    A porta é lida com int(), e não como texto, porque o os.getenv devolve sempre
    texto e o número da porta é número.

    Os valores padrão seguem o mesmo motivo do da origem do front: o back sobe
    mesmo numa máquina sem .env. Quem manda é o valor do .env.
    """
    return URL.create(
        drivername="mysql+mysqlconnector",
        username=os.getenv("BANCO_USUARIO", "root"),
        password=os.getenv("BANCO_SENHA", ""),
        host=os.getenv("BANCO_HOST", "localhost"),
        port=int(os.getenv("BANCO_PORTA", "3306")),
        database=os.getenv("BANCO_NOME", "traco_fino"),
    )
