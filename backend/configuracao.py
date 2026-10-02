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

load_dotenv()


def endereco_do_front() -> str:
    """Devolve o endereço exato do meu front, que é o único liberado no CORS.

    O segundo argumento do os.getenv é um valor padrão, usado só se a chave não
    estiver no .env. Ele existe para o back subir mesmo numa máquina sem .env, e não
    muda nada quando o .env existe: quem manda é o valor de lá.
    """
    return os.getenv("ORIGEM_FRONTEND", "http://localhost:5173")


def endereco_do_banco() -> dict:
    """Devolve os dados de conexão do MySQL, lidos do .env.

    A chave da senha é BANCO_SENHA, e o valor padrão é a string vazia. O valor
    padrão existe pelo mesmo motivo do da origem do front: o back sobe mesmo numa
    máquina sem .env. Quem manda é o valor do .env, e num projeto de verdade o
    .env é o que tem a senha.

    A porta é lida com int(), e não como texto. O pymysql espera a porta como
    número, e o os.getenv devolve sempre texto: sem o int() a conexão falharia.

    Este arquivo devolve um dicionário em vez de vários argumentos soltos porque
    são cinco valores que sempre viajam juntos, e um dicionário não permite
    trocar a ordem deles na chamada.
    """
    return {
        "host": os.getenv("BANCO_HOST", "localhost"),
        "porta": int(os.getenv("BANCO_PORTA", "3306")),
        "banco": os.getenv("BANCO_NOME", "traco_fino"),
        "usuario": os.getenv("BANCO_USUARIO", "root"),
        "senha": os.getenv("BANCO_SENHA", ""),
    }
