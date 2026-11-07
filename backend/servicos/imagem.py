"""A regra das imagens de tatuagem.

Quem envia o quê, qual arquivo serve e o que a aprovação faz com a etapa ficam
aqui. A rota só recebe o corpo binário e escolhe o status HTTP; o depósito só
grava e lê; este serviço é quem recusa o que não vale.

A aprovação do desenho é o ponto central: quando o cliente aprova a imagem do
tipo desenho e a tatuagem ainda está "pedida", o próprio serviço registra o passo
"desenho aprovado" e a etapa anda. O tatuador não digita mais esse passo.
"""

from datetime import datetime, timezone

import repositorios.imagem as repositorio_imagens
from servicos import passo as servico_passos
from servicos.excecoes import (
    AprovacaoDoClienteNecessaria,
    ArquivoDeImagemInvalido,
    ImagemJaAprovada,
    ImagemNaoAprovavel,
    ImagemNaoEncontrada,
    TipoDeImagemDesconhecido,
)


# O limite fica abaixo do teto de 4,5 MB da função da Vercel. O corpo inteiro da
# requisição viaja junto, então o arquivo precisa caber com folga.
TAMANHO_MAXIMO_IMAGEM = 4 * 1024 * 1024

TIPOS_DE_CONTEUDO = {"image/jpeg", "image/png", "image/webp"}

TIPOS_DE_IMAGEM = {"desenho", "referencia"}


def _agora():
    """Devolve o instante atual com fuso, como o PostgreSQL espera."""
    return datetime.now(timezone.utc)


def _validar_tipo(tipo: str) -> str:
    """Confere se o tipo é desenho ou referência, e devolve normalizado."""
    tipo_normalizado = (tipo or "").strip().lower()

    if tipo_normalizado not in TIPOS_DE_IMAGEM:
        raise TipoDeImagemDesconhecido(
            f"'{tipo}' não é um tipo de imagem aceito. "
            "Use 'desenho' ou 'referencia'."
        )

    return tipo_normalizado


def _validar_arquivo(content_type: str, conteudo: bytes) -> str:
    """Confere tamanho e tipo do arquivo, e devolve o content type limpo."""
    tipo_de_conteudo = (content_type or "").split(";")[0].strip().lower()

    if tipo_de_conteudo not in TIPOS_DE_CONTEUDO:
        raise ArquivoDeImagemInvalido(
            "O arquivo precisa ser uma imagem JPEG, PNG ou WebP."
        )

    if not conteudo:
        raise ArquivoDeImagemInvalido("O arquivo da imagem está vazio.")

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
        raise ArquivoDeImagemInvalido(
            "A imagem passa do limite de 4 MB. Envie uma versão menor."
        )

    return tipo_de_conteudo


def listar_imagens(tatuagem_id: int) -> list[dict]:
    """Devolve os metadados das imagens de uma tatuagem."""
    return repositorio_imagens.listar_imagens(tatuagem_id)


def obter_conteudo(tatuagem_id: int, imagem_id: int) -> dict | None:
    """Devolve o arquivo e os dados de download, ou None se não existir."""
    imagem = repositorio_imagens.buscar_conteudo(tatuagem_id, imagem_id)

    if imagem is None:
        return None

    return imagem


def enviar_imagem(
    tatuagem_id: int,
    tatuagem: dict | None,
    usuario: dict,
    nome: str,
    tipo: str,
    content_type: str,
    conteudo: bytes,
) -> dict | None:
    """Grava uma imagem nova, aplicando as regras de quem pode enviar o quê.

    O cliente só envia referência: mesmo que a tela mande "desenho", o serviço
    troca para "referencia". O desenho é upload do tatuador, e a aprovação é uma
    ação separada do cliente.
    """
    if tatuagem is None:
        return None

    tipo_normalizado = _validar_tipo(tipo)
    tipo_de_conteudo = _validar_arquivo(content_type, conteudo)

    if usuario["papel"] == "cliente":
        tipo_normalizado = "referencia"

    nome_limpo = (nome or "").strip()[:255] or "imagem"

    return repositorio_imagens.criar_imagem(
        tatuagem_id,
        {
            "nome": nome_limpo,
            "content_type": tipo_de_conteudo,
            "tamanho_bytes": len(conteudo),
            "tipo": tipo_normalizado,
            "conteudo": conteudo,
        },
    )


def aprovar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    tatuagem: dict | None,
    usuario: dict,
) -> dict | None:
    """Aprova o desenho e, se a etapa ainda é "pedida", registra o passo.

    A validação da regra roda primeiro, para uma tatuagem que não aceite mais o
    passo recusar sem deixar a imagem aprovada pela metade.
    """
    if tatuagem is None:
        return None

    if usuario["papel"] != "cliente":
        raise AprovacaoDoClienteNecessaria(
            "O desenho é aprovado pelo cliente, não pelo tatuador."
        )

    imagem = repositorio_imagens.buscar_imagem(tatuagem_id, imagem_id)

    if imagem is None:
        raise ImagemNaoEncontrada("Essa imagem não existe nesta tatuagem.")

    if imagem["tipo"] != "desenho":
        raise ImagemNaoAprovavel(
            "Só a imagem do tipo desenho pode ser aprovada. "
            "Referências não passam por aprovação."
        )

    # Aprovar de novo não muda a etapa nem cria outro passo. A tela pode repetir
    # a chamada sem duplicar histórico.
    if imagem["status"] == "aprovada":
        return imagem

    # A regra do passo roda antes da gravação do status. Se a tatuagem não está
    # mais "pedida", o serviço de passos recusa aqui e a imagem fica como estava.
    if tatuagem["etapa"] == "pedida":
        servico_passos.aplicar_passo(tatuagem, "desenho aprovado")

    aprovada = repositorio_imagens.aprovar_imagem(
        tatuagem_id,
        imagem_id,
        usuario["id"],
        _agora(),
    )

    # Só a primeira aprovação de um desenho faz a etapa andar. Se a tatuagem já
    # estava em "desenho aprovado" ou além, a imagem é aprovada mas o passo não é
    # repetido.
    if tatuagem["etapa"] == "pedida":
        servico_passos.registrar_passo(
            tatuagem_id,
            {
                "tipo": "desenho aprovado",
                "observacao": f'Desenho "{imagem["nome"]}" aprovado pelo cliente.',
            },
            tatuagem=tatuagem,
            aprovado_pelo_cliente=True,
        )

    return aprovada


def recusar_imagem(
    tatuagem_id: int,
    imagem_id: int,
    motivo: str,
    usuario: dict,
) -> dict | None:
    """Recusa o desenho, guardando o motivo que o cliente escreveu."""
    if usuario["papel"] != "cliente":
        raise AprovacaoDoClienteNecessaria(
            "O desenho é aprovado ou recusado pelo cliente, não pelo tatuador."
        )

    imagem = repositorio_imagens.buscar_imagem(tatuagem_id, imagem_id)

    if imagem is None:
        raise ImagemNaoEncontrada("Essa imagem não existe nesta tatuagem.")

    if imagem["tipo"] != "desenho":
        raise ImagemNaoAprovavel(
            "Só a imagem do tipo desenho pode ser recusada."
        )

    if imagem["status"] == "aprovada":
        raise ImagemJaAprovada(
            "Esse desenho já foi aprovado e não pode mais ser recusado."
        )

    return repositorio_imagens.recusar_imagem(
        tatuagem_id,
        imagem_id,
        (motivo or "").strip()[:500],
        _agora(),
    )


def remover_imagem(tatuagem_id: int, imagem_id: int) -> bool:
    """Remove uma imagem e avisa quando ela não existia na tatuagem."""
    removida = repositorio_imagens.remover_imagem(tatuagem_id, imagem_id)

    if not removida:
        raise ImagemNaoEncontrada("Essa imagem não existe nesta tatuagem.")

    return True
