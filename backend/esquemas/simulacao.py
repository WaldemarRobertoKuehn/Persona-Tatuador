"""Contratos da simulação fictícia de atendimento do estúdio."""

from pydantic import BaseModel, Field


class SimulacaoStudioEntrada(BaseModel):
    """Situação hipotética descrita para iniciar o atendimento."""

    situacao: str = Field(
        min_length=10,
        max_length=1500,
        description="Descrição fictícia do pedido, sem dados pessoais.",
    )


class EtapaSimulacaoSaida(BaseModel):
    """Resumo e fala de uma persona em uma etapa da simulação."""

    etapa: int = Field(ge=1, le=4)
    persona: str
    titulo: str
    resumo: str
    fala: str


class SimulacaoStudioSaida(BaseModel):
    """Resultado completo, não persistido, da simulação."""

    etapas: list[EtapaSimulacaoSaida]
