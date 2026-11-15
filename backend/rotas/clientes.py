"""Rotas de cadastro e listagem de clientes do atendimento presencial."""

from fastapi import APIRouter, Depends, HTTPException

from esquemas.cliente import ClienteEntrada, ClienteSaida
from rotas.dependencias import exigir_permissao
import servicos.cliente as servico_clientes


roteador_clientes = APIRouter(prefix="/clientes", tags=["clientes"])


@roteador_clientes.get(
    "",
    response_model=list[ClienteSaida],
    dependencies=[Depends(exigir_permissao("clientes:consultar"))],
)
def listar_clientes() -> list[dict]:
    """Lista as clientes para o administrador escolher num pedido presencial."""
    return servico_clientes.listar_clientes()


@roteador_clientes.post(
    "",
    response_model=ClienteSaida,
    status_code=201,
    dependencies=[Depends(exigir_permissao("clientes:cadastrar"))],
)
def cadastrar_cliente(dados: ClienteEntrada) -> dict:
    """Cadastra a cliente ou devolve a que já existe com o mesmo nome."""
    try:
        return servico_clientes.cadastrar_cliente(dados.nome)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
