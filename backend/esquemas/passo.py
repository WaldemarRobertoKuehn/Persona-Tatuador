"""Os esquemas Pydantic do passo.

Este arquivo só descreve o formato do passo: o que o front manda ao registrar um
passo e o que o back devolve. A ordem dos passos, que é a regra da cartilha, é do
serviço, não daqui.

São dois esquemas porque entrada e saída são diferentes: a data do passo não vem do
formulário, e o id do passo não existe antes de o passo ser gravado.
"""

from datetime import date

from pydantic import BaseModel, Field


class PassoEntrada(BaseModel):
    """O que o front manda quando Vitor registra um passo numa tatuagem."""

    # tipo é texto livre neste esquema, de propósito. Os três tipos possíveis são
    # "desenho aprovado", "sessão" e "retoque", mas quem decide se o passo é aceito
    # é o serviço, aplicando a regra da cartilha. Se este esquema recusasse o tipo,
    # a recusa viria com 422, e a regra tem de ser recusada pelo serviço, para o
    # front receber o motivo.
    tipo: str = Field(
        min_length=3,
        max_length=30,
        description='O tipo do passo: "desenho aprovado", "sessão" ou "retoque".',
    )

    # default="" quer dizer que a observação é opcional: uma sessão curta pode não
    # ter nada a registrar, e o Vitor não deveria ser obrigado a escrever.
    observacao: str = Field(
        default="",
        max_length=500,
        description="O que foi feito neste passo, nas palavras do tatuador.",
    )


class PassoSaida(BaseModel):
    """O que o back devolve depois de registrar um passo."""

    # id e data não entram no esquema de entrada: o id é dado pelo repositório, e a
    # data é a de hoje, montada pelo serviço no momento do registro.
    id: int = Field(description="Identificador do passo, dado pelo repositório.")

    tatuagem_id: int = Field(
        description="A tatuagem dona deste passo. Não vem no formulário, porque quem "
        "diz qual é é o caminho da rota."
    )

    tipo: str = Field(
        description='O tipo do passo: "desenho aprovado", "sessão" ou "retoque".'
    )

    data: date = Field(description="A data do registro, montada pelo serviço.")

    observacao: str = Field(description="O que foi feito neste passo.")
