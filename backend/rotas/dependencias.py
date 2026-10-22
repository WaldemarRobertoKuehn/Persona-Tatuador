"""NOVO: dependências HTTP que aplicam permissões e escopo de tatuagem."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from rotas.autenticacao import obter_usuario_atual
import servicos.tatuagem as servico_tatuagens


def exigir_permissao(codigo: str) -> Callable[..., dict]:
    """NOVO: cria uma dependência que exige uma permissão específica."""

    def verificar(usuario: dict = Depends(obter_usuario_atual)) -> dict:
        if codigo not in usuario.get("permissoes", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu grupo não tem permissão para esta operação.",
            )
        return usuario

    return verificar


def exigir_uma_permissao(*codigos: str) -> Callable[..., dict]:
    """NOVO: cria uma dependência que aceita qualquer permissão listada."""

    def verificar(usuario: dict = Depends(obter_usuario_atual)) -> dict:
        permissoes = set(usuario.get("permissoes", []))
        if not permissoes.intersection(codigos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu grupo não tem permissão para esta operação.",
            )
        return usuario

    return verificar


def exigir_acesso_a_tatuagem(
    permissao_propria: str,
    permissao_total: str,
) -> Callable[..., dict]:
    """NOVO: verifica permissão e titularidade antes de expor uma tatuagem."""

    def verificar(
        tatuagem_id: int,
        usuario: dict = Depends(obter_usuario_atual),
    ) -> dict:
        permissoes = set(usuario.get("permissoes", []))
        tem_acesso_total = permissao_total in permissoes
        if not tem_acesso_total and permissao_propria not in permissoes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu grupo não tem permissão para esta operação.",
            )

        tatuagem = servico_tatuagens.buscar_tatuagem(tatuagem_id)
        if tatuagem is None:
            raise HTTPException(status_code=404, detail="Tatuagem não encontrada.")
        if (
            not tem_acesso_total
            and tatuagem["cliente_id"] != usuario.get("cliente_id")
        ):
            raise HTTPException(status_code=404, detail="Tatuagem não encontrada.")
        return tatuagem

    return verificar
