"""A decisão de cadastrar uma cliente no atendimento presencial.

A tabela clientes guarda o nome de quem é atendido pelo estúdio. A conta de login
é outra coisa: quem entra no site tem uma linha em usuarios ligada a esta. No
balcão, o administrador só precisa da cliente para pendurar a tatuagem nela, e é
por isso que este serviço não cria conta nem senha.

O cadastro é idempotente pelo nome. Se a cliente já existe, a linha existente é
devolvida em vez de criar uma segunda com o mesmo nome.
"""

import repositorios.cliente as repositorio_clientes


def listar_clientes() -> list[dict]:
    """Devolve as clientes que a administração pode escolher num pedido."""
    return repositorio_clientes.listar_clientes()


def cadastrar_cliente(nome: str) -> dict:
    """Cria a cliente ou devolve a que já tem esse nome."""
    nome_limpo = (nome or "").strip()

    if len(nome_limpo) < 2:
        raise ValueError("O nome da cliente precisa ter pelo menos 2 caracteres.")

    existente = repositorio_clientes.buscar_cliente_por_nome(nome_limpo)
    if existente is not None:
        return existente

    cliente_id = repositorio_clientes.criar_cliente(nome_limpo)
    return {"id": cliente_id, "nome": nome_limpo}
