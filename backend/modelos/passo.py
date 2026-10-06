"""O modelo SQLAlchemy do passo.

O passo é a menor das três tabelas e a única que nunca é procurada sozinha: ela
sempre pertence a uma tatuagem, e é lida como histórico dela. Quem decide se um
passo é aceito, e o que ele faz com a etapa da tatuagem, é o serviço.
"""

# Date é o tipo que vira DATE no MySQL, que é o que o DER pede para o passo: um dia,
# e não um instante. A ficha do Vitor não tem campo de data, e a cartilha fala em
# data, não em horário.
from sqlalchemy import Column, Date, ForeignKey, Integer, String

# O modelo que tem ForeignKey importa o modelo da tabela para onde a chave aponta,
# e este passo aponta para a tatuagem. É este import que registra a tabela
# tatuagens no desenho do SQLAlchemy.
from modelos.tatuagem import Tatuagem

# A Base é a mesma dos outros dois modelos, e vem do banco.py.
from banco import Base


class Passo(Base):
    """A tabela passos: um registro do que foi feito numa tatuagem."""

    __tablename__ = "passos"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # tatuagem_id: de qual tatuagem é o passo. nullable=False porque a cartilha diz
    # que o passo pertence a uma tatuagem, e a rota já sabe de qual é: o id vem do
    # caminho, não do corpo do pedido, para o mesmo passo não poder nascer dono de
    # duas tatuagens.
    #
    # ondelete="CASCADE" vira ON DELETE CASCADE no SQL: se a tatuagem for apagada, os
    # passos dela vão junto, e o banco nunca fica com passo apontando para tatuagem
    # inexistente. A API não apaga tatuagem nenhuma, então isso não roda hoje; fica
    # escrito para o banco não deixar o dado quebrado. Este CASCADE é o do SQL, na
    # chave estrangeira, e não o cascade do ORM, que é outra coisa e não é usado.
    #
    # O name="fk_passos_tatuagem" dá o nome da chave no MySQL, que é o mesmo que o
    # esquema.sql já deu à constraint. Sem o name, o Alembic não sabe desfazer a chave.
    tatuagem_id = Column(
        Integer,
        ForeignKey("tatuagens.id", name="fk_passos_tatuagem", ondelete="CASCADE"),
        nullable=False,
    )

    # tipo: desenho aprovado, sessão ou retoque. VARCHAR(30) pelo mesmo motivo da
    # etapa: a lista dos tipos aceitos é do serviço, e não do banco.
    tipo = Column(String(30), nullable=False)

    # data: o dia do passo. O serviço monta com date.today(), porque a ficha não tem
    # campo de data e quem anota a data é o back.
    data = Column(Date, nullable=False)

    # observacao: o que o Vitor escreveu no registro, e pode ser vazio, porque uma
    # sessão curta nem sempre tem nada a registrar.
    #
    # São dois padrões default com nomes parecidos e lugares diferentes: default=""
    # é o do Python, e preenche o campo no próprio objeto antes de gravar;
    # server_default="" é o do MySQL, e grava DEFAULT '' na tabela, para o banco
    # recusar sozinho um passo sem observação. Com os dois, a coluna nunca chega
    # vazia em nenhum dos lados.
    observacao = Column(
        String(500), nullable=False, default="", server_default=""
    )