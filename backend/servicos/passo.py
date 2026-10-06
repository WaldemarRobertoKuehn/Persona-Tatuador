"""A regra da cartilha, que é a parte que pensa.

Este arquivo decide se um passo é aceito ou recusado, e é o coração do sistema.
A regra vem inteira da cartilha:

    A tatuagem nova começa pedida. Os passos seguem uma ordem: primeiro o desenho
    aprovado, depois uma ou mais sessões, e por fim o retoque, que só acontece
    depois da cicatrização. O serviço recusa sessão antes do desenho aprovado, e
    retoque antes de pelo menos uma sessão. Cada passo aceito muda a etapa.

Como o serviço recusa, e como a rota escolhe o status

O serviço NÃO levanta HTTPException, porque essa exceção pertence à rota, e a
regra do projeto é essa separação. Quando a regra recusa, o serviço levanta uma
exceção própria de servicos/excecoes.py, cujo nome **é** o motivo da recusa, e a
rota pega essa exceção com except e escolhe o status. A tatuagem que não existe
continua sendo None, porque não achar não é recusa de regra: é 404, e quem trata
do 404 é a dependência.

Então esta função devolve duas coisas diferentes, e a recusa nem chega até aqui:

    dict  -> o passo foi aceito e gravado
    None  -> a tatuagem não existe
"""

import repositorios.passo as repositorio_passos
import repositorios.tatuagem as repositorio_tatuagens

# As duas recusas da regra, com o nome de cada motivo. Este arquivo não escreve
# número de status em lugar nenhum: quem escolhe o status é a rota, que pega estas
# exceções com except.
from servicos.excecoes import EtapaNaoAceitaPasso, PassoDesconhecido

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


def aplicar_passo(tatuagem: dict, tipo: str) -> str:
    """A regra da cartilha, e só ela: devolve a etapa que a tatuagem passa a ter.

    A regra ficou nesta função com o nome dela para não ficar espalhada pelo
    registro do passo. Ela faz duas perguntas, na ordem em que a cartilha faz, e
    recusa levantando a exceção do motivo:

        1. esse texto é um passo do estúdio?
        2. a tatuagem está numa etapa que esse passo aceita?

    Quem recusa é o raise, e o raise sai da função ali mesmo: nada abaixo dele
    roda. Por isso o chamador pode chamar aplicar_passo antes de gravar qualquer
    coisa, sabendo que se ela não levantou, o passo entra.

    O que volta é só a etapa nova, em texto. O dicionário REGRAS_DE_PASSO é
    detalhe interno deste arquivo, e quem chama não precisa saber a chave dele:
    pergunta-se "que etapa fica?" e a função responde "esta".
    """
    # A cartilha fecha a lista de passos: desenho aprovado, sessão e retoque. Um
    # tipo fora dessa lista não é um passo, e o problema está no dado que chegou.
    if tipo not in REGRAS_DE_PASSO:
        raise PassoDesconhecido(
            f"'{tipo}' não é um passo deste estúdio. "
            "Os passos são: desenho aprovado, sessão e retoque."
        )

    regra = REGRAS_DE_PASSO[tipo]

    # Aqui está a regra propriamente dita: o passo só entra se a tatuagem estiver
    # numa das etapas que ele aceita. A regra já traz a lista pronta, então a
    # comparação é direta. O dado está bom e a situação é que não deixa, que é o
    # que a rota vai traduzir em 409 em vez de 422.
    if tatuagem["etapa"] not in regra["etapas_aceitas"]:
        raise EtapaNaoAceitaPasso(
            f"Não dá para registrar '{tipo}' agora: a tatuagem está "
            f"'{tatuagem['etapa']}', e esse passo só entra em tatuagem que "
            f"esteja em: {', '.join(regra['etapas_aceitas'])}."
        )

    return regra["etapa_nova"]


def registrar_passo(tatuagem_id: int, dados: dict) -> dict | None:
    """Registra um passo numa tatuagem, se a regra da cartilha deixar.

    Devolve o passo gravado quando a regra aceita, e None quando a tatuagem não
    existe. A recusa da regra não volta: ela sai como exceção de
    servicos/excecoes.py, e quem escolhe o status HTTP é a rota, pegando a
    exceção com except.
    """
    # Primeiro a tatuagem existe? Sem ela não há sobre o que aplicar a regra, e a
    # rota precisa de um None para responder 404.
    tatuagem = repositorio_tatuagens.buscar_tatuagem(tatuagem_id)

    if tatuagem is None:
        return None

    # A regra roda antes de qualquer gravação. Se ela levantar, o passo não foi
    # escrito e a etapa não mudou: o raise sai da função e nada abaixo roda.
    etapa_nova = aplicar_passo(tatuagem, dados["tipo"])

    # Aceito. Primeiro grava o passo, depois muda a etapa, porque a etapa só muda
    # se o passo entrou. A ordem importa: se a gravação do passo falhar, a
    # tatuagem não anda.
    passo = repositorio_passos.criar_passo(tatuagem_id, dados)

    repositorio_tatuagens.atualizar_etapa(tatuagem_id, etapa_nova)

    return passo
