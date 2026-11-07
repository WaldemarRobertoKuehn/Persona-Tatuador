"""A porta de entrada no PostgreSQL, compartilhada pelos três repositórios.

Este arquivo é a única parte do back que sabe que existe um banco de dados, e ele
guarda o engine, a fábrica de sessão, a classe Base e a função cursor() que os
repositórios usam. Os três repositórios não citam driver, conexão nem senha em
lugar nenhum: eles recebem o cursor pronto.

Por que o arquivo existe

    A regra do projeto manda configuracao.py ser o único arquivo que lê o .env, e ela
    cumpre isso: os dados de conexão saem de lá, e não daqui. O que este arquivo faz
    é o passo seguinte, que é abrir a conexão de verdade. Guardar esse passo em
    qualquer um dos três repositórios significaria o mesmo código repetido três
    vezes, e o dia que a senha mudasse de lugar seriam três lugares para mudar. Um
    arquivo só, com o nome do que ele é, é mais honesto do que um pedaço desse passo
    escondido dentro de um repositório.

Por que a conexão nasce uma vez por requisição

    Uma conexão é uma conversa com o banco, e abrir uma conversa custa caro: TCP,
    TLS e autenticação. Se cada função de repositório abrisse a sua, uma rota que
    lê a tatuagem, a cliente e o histórico pagaria esse custo várias vezes. Por
    isso o main.py abre uma conexão no começo da requisição e a guarda no
    ContextVar; cursor() reutiliza essa conexão, e cada bloco ainda confirma ou
    desfaz a sua transação. Fora de uma requisição, cursor() abre e fecha a
    conexão sozinho, o que mantém scripts e testes funcionando.
"""

from contextlib import contextmanager
from contextvars import ContextVar

# create_engine é o que cria o engine: o objeto que sabe falar com o banco e que
# guarda o pool de conexões. O pool é o conjunto de conexões que o SQLAlchemy abre
# e reaproveita, para não abrir uma conexão nova a cada requisição.
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import psycopg2
from psycopg2.extras import RealDictCursor

# sessionmaker é a fábrica de sessões: chamar Sessao() devolve uma sessão nova, e é
# por isso que ela se chama Sessao, com S maiúsculo, como a regra do projeto pede.
from sqlalchemy.orm import sessionmaker

# DeclarativeBase é a classe base de todos os modelos declarativos do SQLAlchemy 2.
# A nossa Base herda dela, e é dessa Base que os modelos de backend/modelos/ herdam
# também. A Base guarda o desenho de todas as tabelas do projeto, e é dela que o
# criar_tabelas.py lê para criar o banco.
from sqlalchemy.orm import DeclarativeBase

# Import de módulo com `import configuracao`: este arquivo não puxa nenhuma função
# solta da configuração, e segue a mesma convenção do main.py.
import configuracao


class Base(DeclarativeBase):
    """A classe base dos modelos, e o lugar onde o desenho das tabelas é guardado."""


# O engine nasce quando este arquivo é importado, e não dentro de função, porque ele
# não muda de requisição para requisição: mudar isso abriria um pool novo a cada
# pedido. O endereço vem do configuracao.py, que é quem leu o .env.
engine = create_engine(
    configuracao.endereco_do_banco(),
    connect_args={"connect_timeout": 5},
    poolclass=NullPool,
)


def _abrir_conexao():
    endereco = configuracao.endereco_do_banco()
    return psycopg2.connect(
        host=endereco.host,
        port=endereco.port,
        user=endereco.username,
        password=endereco.password,
        database=endereco.database,
        sslmode=endereco.query["sslmode"],
        connect_timeout=5,
    )


class _ConexaoDaRequisicao:
    """Guarda a conexão aberta uma vez e reutilizada durante a requisição."""

    def __init__(self):
        self.conexao = None

    def obter(self):
        if self.conexao is None or self.conexao.closed:
            self.conexao = _abrir_conexao()
        return self.conexao

    def fechar(self):
        conexao = self.conexao
        self.conexao = None
        if conexao is not None and not conexao.closed:
            conexao.close()


_conexao_da_requisicao: ContextVar[_ConexaoDaRequisicao | None] = ContextVar(
    "conexao_da_requisicao",
    default=None,
)


def iniciar_conexao_da_requisicao():
    """Marca o início da requisição que vai compartilhar uma única conexão."""
    return _conexao_da_requisicao.set(_ConexaoDaRequisicao())


def encerrar_conexao_da_requisicao(token):
    """Fecha a conexão da requisição e restaura o estado anterior."""
    estado = _conexao_da_requisicao.get()
    if estado is not None:
        estado.fechar()
    _conexao_da_requisicao.reset(token)


@contextmanager
def cursor():
    """Abre um cursor PostgreSQL em formato de dicionário para os repositórios."""
    estado = _conexao_da_requisicao.get()
    conexao_propria = estado is None
    conexao = _abrir_conexao() if conexao_propria else estado.obter()

    try:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor_banco:
            yield cursor_banco
        conexao.commit()
    except Exception:
        try:
            conexao.rollback()
        except Exception:
            pass
        if not conexao_propria and conexao.closed:
            estado.conexao = None
        raise
    finally:
        if conexao_propria:
            conexao.close()


# Sessao é a fábrica, e não a sessão: o nome Sessao() na rota entrega uma sessão
# nova por requisição. É o mesmo nome que a regra do projeto pede.
Sessao = sessionmaker(bind=engine)


# obter_sessao é a função que o Depends da rota chama. É o único lugar do projeto que
# cria sessão, e a regra é essa: nenhuma função de repositório abre sessão com
# Sessao() por conta própria.
def obter_sessao():
    # O with garante que a sessão seja fechada ao final da requisição, mesmo se a
    # rota levantar um erro no meio. Fechar sem commit é o que desfaz o que foi
    # gravado, e é o rollback de que a regra fala: a regra que muda mais de uma
    # tabela grava tudo num commit só, e erro antes do commit desfaz tudo.
    with Sessao() as sessao:
        # yield é o que entrega a sessão à rota e segura a função aberta até a rota
        # terminar. Quem recebe a sessão no Depends é quem decide a transação.
        yield sessao
