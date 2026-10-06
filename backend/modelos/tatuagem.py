"""O modelo SQLAlchemy da tatuagem.

Este é o modelo do meio das três tabelas, e o único que tem duas ligações: a
tatuagem aponta para uma cliente e guarda os passos dela dentro dela. A etapa, que
é o campo mais importante da tabela, é escrita pelo serviço e nunca pelo front.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

# ForeignKey, no nome da tabela como texto, é o que cria a ligação entre as tabelas
# e diz qual é a coluna que aponta para qual: "clientes.id" quer dizer que a coluna
# cliente_id desta tabela aponta para a coluna id da tabela clientes.
#
# Numeric é o tipo que vira DECIMAL no MySQL, e o que segura o tamanho exato da
# tatuagem em centímetros.

# O modelo que tem ForeignKey importa o modelo da tabela para onde a chave aponta.
# Não é vaidade: é esse import que registra a tabela clientes no desenho do
# SQLAlchemy. E o passo, que também tem ForeignKey, importa este arquivo, e não o
# contrário, para os dois arquivos não se importarem um ao outro em círculo.
from modelos.cliente import Cliente

# A Base é a mesma dos outros dois modelos, e vem do banco.py. A classe Tatuagem
# herda dela, que é o que registra esta tabela no desenho do SQLAlchemy.
from banco import Base


class Tatuagem(Base):
    """A tabela tatuagens: o pedido da cliente e em que etapa ele está."""

    __tablename__ = "tatuagens"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # cliente_id: de quem é a tatuagem. A ForeignKey é o que impede uma tatuagem sem
    # dona, que é o tipo de dado quebrado que ninguém percebe até a tela abrir em
    # branco. nullable=False porque a cartilha diz que a tatuagem pertence a um
    # cliente: não existe tatuagem sem dona.
    #
    # O name="fk_tatuagens_cliente" é o nome da chave no MySQL, e ele não é enfeite:
    # sem ele o Alembic não sabe o nome da restrição que criou, e avisa que não
    # consegue desfazer a chave numa migration. É o mesmo nome que o esquema.sql já
    # deu à constraint, e o mesmo que a migration usa no op.create_foreign_key.
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", name="fk_tatuagens_cliente"),
        nullable=False,
    )

    # ideia: o que a Bruna descreveu no celular, com as palavras dela. O VARCHAR(500)
    # é o mesmo max_length do esquema de entrada, e os dois lados barrando no mesmo
    # número é o que a régua do REST pede.
    ideia = Column(String(500), nullable=False)

    # local_do_corpo: onde vai ser tatuado. VARCHAR(80) porque é uma frase curta.
    local_do_corpo = Column(String(80), nullable=False)

    # tamanho: o tamanho em centímetros, com duas casas decimais. Numeric(6, 2) é o
    # DECIMAL(6,2) do DER: seis dígitos no total, sendo dois depois do ponto, então o
    # maior valor possível é 9999.99. Serve Decimal e não FLOAT porque tamanho é
    # medida, e medida não aceita erro de ponto flutuante: 12.5 volta 12.50, e não
    # 12.499999.
    #
    # Uma consequência que vale saber: do banco, tamanho volta como Decimal do
    # Python, e não como float. O esquema de saída declara float, e o Pydantic
    # converte o Decimal sozinho na hora de montar a resposta.
    tamanho = Column(Numeric(precision=6, scale=2), nullable=False)

    # etapa: pedida, desenho aprovado, em sessões ou finalizada. VARCHAR(30) e não
    # ENUM de propósito: esses quatro textos já estão escritos em servicos/passo.py,
    # e a regra de quando uma etapa pode virar outra é do serviço. Se o banco também
    # validasse o texto, a mesma lista estaria em dois lugares, e o dia que alguém
    # mudasse num esquecesse do outro.
    etapa = Column(String(30), nullable=False)

    # relationship liga a tatuagem aos passos dela, para o histórico ser lido com
    # ponto: tatuagem.passos. O nome da classe vai como texto entre aspas, e não
    # como import, porque o Passo está num arquivo que importa este: importar aqui
    # criaria um ciclo. O SQLAlchemy acha a classe pelo nome quando este arquivo é
    # carregado ao lado do passo, que é o que o criar_tabelas.py faz.
    #
    # A tabela Tattoagem é a principal deste relacionamento, e por isso é aqui que o
    # relationship mora. Na tabela Cliente não há relationship porque nada precisa
    # ler cliente.tatuagens com ponto: quem busca as tatuagens de uma cliente filtra
    # por cliente_id na consulta, e é mais barato assim.
    passos = relationship("Passo")