"""Os esquemas Pydantic da tatuagem.

Este arquivo só descreve o formato: o que o front manda e o que o back devolve.
Ele não decide nada. A regra da cartilha, que sabe quando um passo muda a etapa,
vive no serviço, e a lista em memória vive no repositório.

São dois esquemas, e não um só, porque entrada e saída não são a mesma coisa:
na entrada o id e a etapa não existem ainda, porque quem os dá é o repositório e a
regra do serviço.
"""

from pydantic import BaseModel, Field


class TatuagemEntrada(BaseModel):
    """O que o front manda quando Bruna pede uma tatuagem nova."""

    # cliente_id: a tela da Bruna diz quem ela é na própria requisição, porque
    # enquanto não existe login é assim que o back sabe de quem é a tatuagem.
    cliente_id: int = Field(gt=0, description="Quem pediu a tatuagem.")

    # min_length e max_length são restrições de tamanho de texto do Pydantic: se a
    # ideia vier vazia ou gigante, o back responde 422 antes de gravar qualquer coisa.
    ideia: str = Field(
        min_length=10,
        max_length=500,
        description="A ideia descrita pela cliente, com as palavras dela.",
    )

    local_do_corpo: str = Field(
        min_length=2,
        max_length=80,
        description="Onde vai ser tatuado, no corpo dela.",
    )

    # gt=0 significa "maior que zero": tamanho zero não é tattoo nenhuma, então
    # o Pydantic barra antes do serviço precisar conferir.
    tamanho: float = Field(gt=0, description="O tamanho combinado, em centímetros.")


class TatuagemSaida(BaseModel):
    """O que o back devolve quando alguém olha uma tatuagem."""

    # id e etapa não entram no esquema de entrada de propósito: o id é sorteado pelo
    # repositório e a etapa é mudada pela regra do serviço, e nenhum dos dois é
    # decisão do front.
    id: int = Field(description="Identificador da tatuagem, dado pelo repositório.")

    cliente_id: int = Field(description="De quem é esta tatuagem.")

    # nome_da_cliente é o mesmo dado de cliente_id, já escrito com letras, porque a
    # agenda do Vitor precisa mostrar o nome e não o número. O front não adivinha o
    # nome a partir do id: o id é uma referência, e quem guarda o dado é o back.
    nome_da_cliente: str = Field(
        description="O nome da cliente dona desta tatuagem."
    )

    ideia: str = Field(description="A ideia pedida pela cliente.")

    local_do_corpo: str = Field(description="Onde vai ser tatuado.")

    tamanho: float = Field(description="O tamanho combinado, em centímetros.")

    etapa: str = Field(
        description=(
            "A etapa atual. Só existem quatro, nesta ordem: pedida, desenho aprovado, "
            "em sessões e finalizada. É o serviço que muda este valor, nunca o front."
        )
    )
