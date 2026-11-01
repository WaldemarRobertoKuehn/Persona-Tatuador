"""Leitura do .env.

Este arquivo é o único do projeto que lê variável de ambiente, porque a regra do
projeto é assim: o que muda de máquina para máquina entra no .env, e a leitura dele
fica concentrada aqui. Por isso nenhuma rota, nenhum serviço e nenhum repositório
chama os.getenv: todos pedem o valor a este arquivo.
"""

import os
from pathlib import Path

# load_dotenv() lê o arquivo .env e coloca cada chave dele como variável de ambiente
# do processo. Sem essa chamada, o os.getenv lá embaixo não encontraria nada.
from dotenv import load_dotenv

# URL é a classe do SQLAlchemy que representa o endereço do banco já em partes:
# driver, usuário, senha, host, porta e nome. Montar o endereço com URL.create, em
# vez de escrever o texto na mão, é o que resolve o problema da senha com caractere
# estranho: o SQLAlchemy escapa o valor na hora de montar o texto, e não a gente.
from sqlalchemy.engine import URL, make_url

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def endereco_do_front() -> str:
    """Devolve o endereço exato do meu front, que é o único liberado no CORS.

    O segundo argumento do os.getenv é um valor padrão, usado só se a chave não
    estiver no .env. Ele existe para o back subir mesmo numa máquina sem .env, e não
    muda nada quando o .env existe: quem manda é o valor de lá.
    """
    return os.getenv("ORIGEM_FRONTEND", "http://localhost:5173").rstrip("/")


def endereco_do_banco() -> URL:
    """Devolve o endereço do PostgreSQL como URL, montado a partir do .env.

    O endereço é devolvido em partes e não como um texto pronto, e o motivo é a
    senha: o .env é um arquivo texto, e a senha pode ter @, : ou /, que são os
    caracteres que separam as partes do endereço. Escrevendo o endereço inteiro num
    só texto, o SQLAlchemy não teria como saber onde acaba a senha, e a conexão
    falharia. Com URL.create, cada parte entra no seu lugar, com o nome do
    argumento, e quem monta o texto é o SQLAlchemy.

    drivername é o par driver+dialeto, escrito no formato do SQLAlchemy. O driver
    psycopg2 é usado tanto pelos repositórios como pelo SQLAlchemy.

    A porta é lida com int(), e não como texto, porque o os.getenv devolve sempre
    texto e o número da porta é número.

    Os valores padrão seguem o mesmo motivo do da origem do front: o back sobe
    mesmo numa máquina sem .env. Quem manda é o valor do .env.
    """
    supabase_url = os.getenv("SUPABASE_DB_URL", "").strip()
    supabase_password = os.getenv("SUPABASE_DB_PASSWORD", "")

    if supabase_url:
        url = make_url(supabase_url)
        return url.set(
            drivername="postgresql+psycopg2",
            password=supabase_password or url.password,
            query={**url.query, "sslmode": os.getenv("BANCO_SSLMODE", "require")},
        )

    return URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("BANCO_USUARIO", "postgres"),
        password=os.getenv("BANCO_SENHA", ""),
        host=os.getenv("BANCO_HOST", "localhost"),
        port=int(os.getenv("BANCO_PORTA", "5432")),
        database=os.getenv("BANCO_NOME", "postgres"),
        query={"sslmode": os.getenv("BANCO_SSLMODE", "require")},
    )


def segredo_token() -> str:
    """Devolve o segredo local usado para assinar os tokens de acesso."""
    segredo = os.getenv("JWT_SEGREDO", "")
    if len(segredo) < 32:
        raise ValueError("Configure JWT_SEGREDO com ao menos 32 caracteres no .env.")
    return segredo


def validade_token_segundos() -> int:
    """Devolve a validade do token, em segundos."""
    minutos = int(os.getenv("JWT_MINUTOS", "60"))
    if minutos < 1:
        raise ValueError("JWT_MINUTOS precisa ser maior que zero.")
    return minutos * 60
