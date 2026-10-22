"""Cria as tabelas do banco vazio, a partir dos modelos.

Uma vez por projeto: roda com `python criar_tabelas.py`, de dentro de backend/,
num banco que ainda não tem as tabelas. Depois que o banco tem dado, mudança no
desenho é migration (alembic upgrade head), e não este arquivo: o create_all não
toca em tabela que já existe.
"""

# A Base e o engine saem do banco.py, o mesmo arquivo de onde a API e o Alembic
# tiram a conexão.
from banco import Base, engine

# Um import por modelo do projeto, igual ao do migracoes/env.py. O import não é
# vaidade: é ele que registra cada tabela na Base.metadata, e é dessa metadata
# que o create_all abaixo lê o desenho. Sem os imports, a metadata chegaria
# vazia e nenhuma tabela seria criada.
from modelos import cliente, grupo, passo, tatuagem, usuario

# create_all cria só as tabelas que ainda não existem: as que já existem ele não
# toca. É o que faz deste arquivo o caminho do banco vazio, e do Alembic o
# caminho do banco que já tem dado.
Base.metadata.create_all(engine)
