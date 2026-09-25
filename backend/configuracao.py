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
