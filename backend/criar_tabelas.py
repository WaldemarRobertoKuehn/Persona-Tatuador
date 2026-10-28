"""Aplica as migrations do banco.

Rode com `python criar_tabelas.py`, de dentro de backend/. O Alembic cria as
tabelas que faltam, registra a revisão aplicada e provisiona os dados iniciais.
"""

from alembic import command
from alembic.config import Config


command.upgrade(Config("alembic.ini"), "head")
