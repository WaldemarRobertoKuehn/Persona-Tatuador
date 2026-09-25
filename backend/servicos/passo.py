"""A regra da cartilha, que é a parte que pensa.

Este arquivo decide se um passo é aceito ou recusado, e é o coração do sistema.
A regra vem inteira da cartilha:

    A tatuagem nova começa pedida. Os passos seguem uma ordem: primeiro o desenho
    aprovado, depois uma ou mais sessões, e por fim o retoque, que só acontece
    depois da cicatrização. O serviço recusa sessão antes do desenho aprovado, e
    retoque antes de pelo menos uma sessão. Cada passo aceito muda a etapa.

Como o serviço recusa, e como a rota escolhe o status

O serviço NÃO levanta HTTPException, porque essa exceção pertence à rota, e a
regra do projeto é essa separação. Quando a regra recusa, o serviço devolve o
texto do motivo, e a rota testa esse texto com if e decide o status. Quando a
tatuagem nem existe, o serviço devolve None, e a rota decide o 404. Então esta
função devolve três tipos diferentes, e a diferença está no tipo do que volta:

    dict  -> o passo foi aceito e gravado
    str   -> a regra recusou, e a string é o motivo
    None  -> a tatuagem não existe
"""

import repositorios.passo as repositorio_passos
import repositorios.tatuagem as repositorio_tatuagens

# A regra da cartilha escrita como tabela, para caber num lugar só e ser fácil de
# defender na apresentação. Cada linha diz em que etapas o passo é aceito e para
# onde a tatuagem vai quando ele é aceito.
#
# Repare em dois detalhes que a cartilha separa e que costumam dar problema: o
# tipo do passo é "sessão", com til, e a etapa é "em sessões", com s. São textos
# diferentes, e o front tem que mandar o tipo exatamente como está escrito aqui.
# E "desenho aprovado" aparece nas duas colunas, como tipo de passo e como nome
# de etapa, e ainda assim são coisas diferentes.
REGRAS_DE_PASSO = {
    "desenho aprovado": {
        "etapas_aceitas": ["pedida"],
        "etapa_nova": "desenho aprovado",
    },
    "sessão": {
        "etapas_aceitas": ["desenho aprovado", "em sessões"],
        "etapa_nova": "em sessões",
    },
    "retoque": {
        "etapas_aceitas": ["em sessões"],
        "etapa_nova": "finalizada",
    },
}


def listar_passos(tatuagem_id: int) -> list[dict]:
    """Devolve o histórico de passos de uma tatuagem, na ordem em que entraram.

    Aqui não há regra a aplicar: a cartilha só pede mostrar o histórico, e o
    depósito já devolve os passos na ordem em que foram gravados.
    """
    return repositorio_passos.listar_passos(tatuagem_id)


def registrar_passo(tatuagem_id: int, dados: dict) -> dict | str | None:
    """Registra um passo numa tatuagem, se a regra da cartilha deixar.

    Devolve o passo gravado quando a regra aceita, o motivo quando a regra
    recusa, e None quando a tatuagem não existe. Quem escolhe o status HTTP é a
    rota, testando o tipo do que voltou com if.
    """
    # Primeiro a tatuagem existe? Sem ela não há sobre o que aplicar a regra, e a
    # rota precisa de um None para responder 404.
    tatuagem = repositorio_tatuagens.buscar_tatuagem(tatuagem_id)

    if tatuagem is None:
        return None

    tipo = dados["tipo"]

    # A cartilha fecha a lista de passos: desenho aprovado, sessão e retoque. Um
    # tipo fora dessa lista não é um passo, e a resposta é o motivo da recusa.
    if tipo not in REGRAS_DE_PASSO:
        return (
            f"'{tipo}' não é um passo deste estúdio. "
            "Os passos são: desenho aprovado, sessão e retoque."
        )

    regra = REGRAS_DE_PASSO[tipo]

    # Aqui está a regra propriamente dita: o passo só entra se a tatuagem estiver
    # numa das etapas que ele aceita. A regra já traz a lista pronta, então a
    # comparação é direta.
    if tatuagem["etapa"] not in regra["etapas_aceitas"]:
        return (
            f"Não dá para registrar '{tipo}' agora: a tatuagem está "
            f"'{tatuagem['etapa']}', e esse passo só entra em tatuagem que "
            f"esteja em: {', '.join(regra['etapas_aceitas'])}."
        )

    # Aceito. Primeiro grava o passo, depois muda a etapa, porque a etapa só muda
    # se o passo entrou. A ordem importa: se a gravação do passo falhar, a
    # tatuagem não anda.
    passo = repositorio_passos.criar_passo(tatuagem_id, dados)

    repositorio_tatuagens.atualizar_etapa(tatuagem_id, regra["etapa_nova"])

    return passo
