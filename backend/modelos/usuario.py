"""O modelo SQLAlchemy da conta de usuário.

A conta é a pessoa que entra no sistema, e ela pertence a um grupo: Cliente,
Tatuador ou Administrador. O vínculo e as permissões moram no banco, e o backend
é quem decide o que cada pessoa pode acessar.

Por que a conta é uma tabela só dela

    Antes a conta morava na tabela clientes, com as colunas email e senha_hash.
    Isso misturava duas coisas do negócio: quem é dona de tatuagem e quem tem
    senha para entrar. O tatuador é dono do estúdio e não é dona de nenhuma
    tatuagem, e mesmo assim precisava de uma linha em clientes só para ter
    login. Com a tabela usuarios, a cliente continua em clientes e a conta fica
    em usuarios, e o elo entre as duas é a coluna cliente_id.

O que a coluna cliente_id faz

    Ela liga a conta do grupo "cliente" à linha dela na tabela clientes, que é
    onde o nome da dona da tatuagem mora. É por essa coluna que "minhas
    tatuagens" filtra por cliente_id, e é por isso que a conta do tatuador
    deixa a coluna vazia: tatuador não é dono de tatuagem.
"""

# Column é o que transforma um atributo desta classe em coluna da tabela, com o
# tipo e a restrição. primary_key=True marca a chave primária, nullable=False vira
# NOT NULL no banco, e UniqueConstraint vira o índice único do email.
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

# A Base é a do banco.py, e não a DeclarativeBase de novo: é dela que o
# criar_tabelas.py e o Alembic leem o desenho de todas as tabelas do projeto.
from banco import Base


class Usuario(Base):
    """A tabela usuarios: a conta que entra no sistema."""

    # __tablename__ diz o nome real da tabela dentro do MySQL. A classe se chama
    # Usuario, no singular, e a tabela se chama usuarios, no plural: é a convenção
    # do projeto.
    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("email", name="uq_usuarios_email"),)

    # id: a chave primária. autoincrement=True diz que quem escolhe o próximo número
    # é o MySQL, e não o código.
    id = Column(Integer, primary_key=True, autoincrement=True)

    # nome: o nome da pessoa, o mesmo que aparece na barra do alto da tela.
    nome = Column(String(100), nullable=False)

    # email: o login. UniqueConstraint diz que dois usuários não podem ter o mesmo
    # email, e o índice único é o que o banco usa para recusar o cadastro repetido
    # sem precisar varrer a tabela.
    email = Column(String(254), nullable=False)

    # senha_hash: a senha guardada como hash, nunca como texto. O hash é o que o
    # argon2id devolve, e é o que a função verificar_senha compara com a senha
    # digitada na tela.
    senha_hash = Column(String(255), nullable=False)

    # papel: compatibilidade com o front existente; o grupo vinculado é a fonte
    # de verdade para autorização e este campo recebe o código do grupo.
    papel = Column(String(50), nullable=False)

    # NOVO: grupo_id liga a conta ao grupo que concede suas permissões de rota.
    grupo_id = Column(
        Integer,
        ForeignKey("grupos.id", name="fk_usuarios_grupo"),
        nullable=False,
    )

    # cliente_id: o elo com a tabela clientes, e ele é vazio para o tatuador.
    # ForeignKey aponta para a chave da tabela de destino, e o nome da
    # constraint é o que permite recriar a chave numa tabela que já existe.
    cliente_id = Column(Integer, ForeignKey("clientes.id", name="fk_usuarios_cliente"))
