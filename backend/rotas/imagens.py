"""As rotas das imagens de uma tatuagem.

O upload recebe o arquivo cru no corpo da requisição, com o nome e o tipo nos
parâmetros de consulta. Isso evita a dependência python-multipart e mantém o
front simples: ele manda o File direto e o Content-Type do arquivo.

O download também passa por aqui, com autenticação. O front não pode usar a URL
direto num <img> porque o navegador não manda o cabeçalho Authorization; por isso
ele busca o arquivo com o token e cria um object URL na tela.
"""

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from esquemas.imagem import ImagemRecusaEntrada, ImagemSaida
from rotas.dependencias import exigir_acesso_a_tatuagem, exigir_permissao
import servicos.imagem as servico_imagens
from servicos.excecoes import (
    AprovacaoDoClienteNecessaria,
    ArquivoDeImagemInvalido,
    EtapaNaoAceitaPasso,
    ImagemJaAprovada,
    ImagemNaoAprovavel,
    ImagemNaoEncontrada,
    TipoDeImagemDesconhecido,
)

# O prefixo já carrega o id da tatuagem, então todas as rotas daqui são de uma
# tatuagem só.
roteador_imagens = APIRouter(
    prefix="/tatuagens/{tatuagem_id}/imagens",
    tags=["imagens"],
)


def _traduzir_erro(erro: Exception) -> None:
    """Converte a recusa do serviço no status HTTP correspondente."""
    if isinstance(erro, (TipoDeImagemDesconhecido, ArquivoDeImagemInvalido)):
        raise HTTPException(status_code=422, detail=str(erro))

    if isinstance(erro, AprovacaoDoClienteNecessaria):
        raise HTTPException(status_code=403, detail=str(erro))

    if isinstance(erro, (ImagemNaoAprovavel, ImagemJaAprovada, EtapaNaoAceitaPasso)):
        raise HTTPException(status_code=409, detail=str(erro))

    if isinstance(erro, ImagemNaoEncontrada):
        raise HTTPException(status_code=404, detail=str(erro))

    raise erro


# A leitura acompanha o acesso à tatuagem: quem pode ver a ficha pode ver as
# imagens dela.
@roteador_imagens.get("", response_model=list[ImagemSaida])
def listar_imagens(
    tatuagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
) -> list[dict]:
    """Lista só os metadados, sem carregar os bytes das imagens."""
    return servico_imagens.listar_imagens(tatuagem_id)


# Enviar exige a permissão de imagem e o acesso à tatuagem. O corpo é lido cru
# porque o arquivo é binário e não precisa de formulário multipart.
@roteador_imagens.post("", response_model=ImagemSaida, status_code=201)
async def enviar_imagem(
    tatuagem_id: int,
    request: Request,
    nome: str = Query(default="imagem", max_length=255),
    tipo: str = Query(default="desenho", max_length=20),
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("imagens:enviar")),
) -> dict:
    """Grava a imagem enviada e devolve os metadados dela."""
    conteudo = await request.body()
    content_type = request.headers.get("content-type", "")

    try:
        imagem = servico_imagens.enviar_imagem(
            tatuagem_id,
            tatuagem,
            usuario,
            nome,
            tipo,
            content_type,
            conteudo,
        )
    except (
        TipoDeImagemDesconhecido,
        ArquivoDeImagemInvalido,
    ) as erro:
        _traduzir_erro(erro)

    return imagem


# O download devolve o arquivo em si. O nome do tatuador e os metadados ficam na
# listagem, para não repetir tudo em cada imagem carregada.
@roteador_imagens.get("/{imagem_id}")
def baixar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
) -> Response:
    """Devolve os bytes da imagem, com o tipo de mídia que foi gravado."""
    imagem = servico_imagens.obter_conteudo(tatuagem_id, imagem_id)

    if imagem is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")

    nome = (imagem["nome"] or "imagem").replace('"', "")

    # O cabeçalho HTTP não aceita acento direto. O filename* com UTF-8 permite
    # nomes como "leão.png"; o filename simples fica como queda para navegador
    # antigo.
    return Response(
        content=bytes(imagem["conteudo"]),
        media_type=imagem["content_type"],
        headers={
            "Content-Disposition": (
                f"inline; filename=\"imagem\"; filename*=UTF-8''{quote(nome)}"
            ),
            "Cache-Control": "private, max-age=300",
        },
    )


# O cliente aprova o desenho. O serviço é quem registra o passo e muda a etapa.
@roteador_imagens.post("/{imagem_id}/aprovacao", response_model=ImagemSaida)
def aprovar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("imagens:aprovar")),
) -> dict:
    """Aprova o desenho e devolve a imagem com o status atualizado."""
    try:
        imagem = servico_imagens.aprovar_imagem(
            tatuagem_id,
            imagem_id,
            tatuagem,
            usuario,
        )
    except (
        AprovacaoDoClienteNecessaria,
        ImagemNaoAprovavel,
        ImagemJaAprovada,
        ImagemNaoEncontrada,
        EtapaNaoAceitaPasso,
    ) as erro:
        _traduzir_erro(erro)

    return imagem


# A recusa guarda o motivo, que fica visível para o tatuador na ficha.
@roteador_imagens.post("/{imagem_id}/recusa", response_model=ImagemSaida)
def recusar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    dados: ImagemRecusaEntrada,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("imagens:aprovar")),
) -> dict:
    """Recusa o desenho e devolve a imagem com o motivo gravado."""
    try:
        imagem = servico_imagens.recusar_imagem(
            tatuagem_id,
            imagem_id,
            dados.motivo,
            usuario,
        )
    except (
        AprovacaoDoClienteNecessaria,
        ImagemNaoAprovavel,
        ImagemJaAprovada,
        ImagemNaoEncontrada,
    ) as erro:
        _traduzir_erro(erro)

    return imagem


# Remover é exclusivo do tatuador. A resposta não tem corpo.
@roteador_imagens.delete("/{imagem_id}", status_code=204)
def remover_imagem(
    tatuagem_id: int,
    imagem_id: int,
    tatuagem: dict = Depends(
        exigir_acesso_a_tatuagem(
            "tatuagens:consultar_propria",
            "tatuagens:consultar_todas",
        )
    ),
    usuario: dict = Depends(exigir_permissao("imagens:remover")),
) -> Response:
    """Apaga a imagem e devolve 204 quando ela existia."""
    try:
        servico_imagens.remover_imagem(tatuagem_id, imagem_id)
    except ImagemNaoEncontrada as erro:
        _traduzir_erro(erro)

    return Response(status_code=204)
