"""O modelo SQLAlchemy da cliente.

Modelo é a classe que descreve a tabela para o SQLAlchemy, e ele vive em
backend/modelos/. Ele não guarda regra de negócio: o que decide em que etapa uma
tatuagem está é o serviço. O que o modelo faz é dizer ao banco quais colunas
existem, com que tipo e com que restrição, exatamente como está no docs/DER.md.
"""

# Column é o que transforma um atributo desta classe em coluna da tabela, com o
# tipo e a restrição. primary_key=True marca a chave primária, nullable=False vira
# NOT NULL no banco, e é por aí que o DER chega no MySQL.
from sqlalchemy import Column, Integer, String, UniqueConstraint

# DeclarativeBase não entra aqui: o que entra é a Base que já foi declarada no
# banco.py, porque é ela que guarda o desenho de todas as tabelas do projeto, e é
# dela que o criar_tabelas.py lê para criar o banco. Cada modelo é uma classe que
# nasce dessa Base.
from banco import Base


class Cliente(Base):
    """A tabela clientes: a pessoa que usa o sistema."""

    # __tablename__ diz o nome real da tabela dentro do MySQL. A classe se chama
    # Cliente, no singular, e a tabela se chama clientes, no plural: é a convenção
    # do projeto, e o que o SQL usa é sempre o que está escrito aqui.
    __tablename__ = "clientes"
    __table_args__ = (UniqueConstraint("email", name="uq_clientes_email"),)

    # id: a chave primária. autoincrement=True diz que quem escolhe o próximo número
    # é o MySQL, e não o código, e é o que transforma a coluna em INT AUTO_INCREMENT.
    id = Column(Integer, primary_key=True, autoincrement=True)

    # nome: o nome da pessoa. VARCHAR(100) é o mesmo limite do max_length do esquema
    # Pydantic, e nullable=False recusa linha sem nome, que é o mesmo cuidado que o
    # esquema de saída tem ao exigir string.
    nome = Column(String(100), nullable=False)

    # Campos de autenticação. Permanecem nulos para preservar os registros antigos
    # até que cada pessoa cadastre email e senha.
    email = Column(String(254), nullable=True)
    senha_hash = Column(String(255), nullable=True)
