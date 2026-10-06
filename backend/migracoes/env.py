"""Onde o Alembic acha os modelos e o banco.

Este arquivo é a ponte entre o Alembic e o projeto. Ele é o que o comando
`alembic upgrade head` executa por baixo, e por isso é o único lugar do projeto
onde o Alembic encontra o desenho das tabelas e o endereço do MySQL.

As duas configuração que interessam

    target_metadata   é o desenho que o Alembic compara com o banco. Aqui ele é a
                      Base.metadata do banco.py, que é exatamente o mesmo desenho
                      que o criar_tabelas.py usa. Sem esta linha, o autogenerate não
                      tem o que comparar e escreve uma migration vazia.

    connectable       é a conexão que o Alembic usa para falar com o MySQL. Aqui ela
                      é o engine do banco.py, e não um engine novo montado a partir
                      do alembic.ini. O motivo é a senha: o endereço, com a senha,
                      é lido do .env pelo configuracao.py, e deste jeito ela não vai
                      para o alembic.ini, que é um arquivo versionado no Git.

O que o Alembic descobre lendo os modelos

    Os três imports abaixo não são vaidade. O Alembic não sabe o que é uma tabela do
    Traço Fino: ele só conhece o desenho que estiver registrado na Base.metadata no
    momento em que o arquivo é lido, e o que registra uma tabela nesse desenho é o
    fato de o arquivo do modelo ter sido importado. Sem os imports, a Base.metadata
    chegaria vazia no Alembic, e a comparação com o banco não teria o que comparar.
"""

from logging.config import fileConfig

from alembic import context

# A Base e o engine saem do banco.py, o mesmo arquivo de onde a API tira a conexão.
from banco import Base, engine

# Um import por modelo do projeto. Os nomes são o caminho dentro de modelos/:
# cliente.py, tatuagem.py e passo.py.
from modelos import cliente, passo, tatuagem

# config é o objeto que lê o alembic.ini, o arquivo de configuração do Alembic.
config = context.config

# Interpreta o arquivo de configuração do Python para o log do Alembic sair no
# terminal no mesmo formato do resto do projeto, e é o que permite ligar o
# sqlalchemy.echo no ini para ver cada comando que ele manda ao MySQL.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# target_metadata é o desenho das tabelas que o autogenerate compara com o banco.
# Substitui o `target_metadata = None` que o `alembic init` deixou aqui.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Roda a migration sem abrir conexão, escrevendo o SQL no terminal.

    Este modo não é usado no projeto: ele existe para quem quer ler o comando que o
    Alembic vai executar sem precisar de banco nenhum. O `alembic current` e o
    `alembic upgrade head` do dia a dia passam pelo run_migrations_online.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Roda a migration falando com o MySQL de verdade.

    O connectable é o engine do banco.py, e não o engine_from_config que o
    `alembic init` deixou aqui. A troca é o que tira a senha do caminho: o
    engine_from_config leria sqlalchemy.url do alembic.ini, e o endereço do banco
    está no .env, lido pelo configuracao.py.
    """
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# context.is_offline_mode() pergunta se o comando quer SQL impresso ou migration
# aplicada. No dia a dia é a segunda opção, e quem roda é o run_migrations_online.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()