"""Os motivos de recusa da regra da cartilha, cada um com o nome dele.

Este arquivo é o lugar onde a regra ganha voz. Cada classe aqui é **um motivo
pelo qual o serviço recusa**, e o nome da classe é esse motivo. É só isso que a
classe guarda: o nome. Quem carrega o texto que aparece na tela é quem levanta,
com `raise Motivo("a frase aqui")`.

Por que uma classe por motivo, e não um `return None` só

    O `return None` diz que a regra recusou, mas não diz por quê, e obriga a rota a
    adivinhar o motivo para escolher o status. Quando os motivos são diferentes,
    os status são diferentes também, e o status é a diferença que o front vê: 422
    diz "corrige o que você mandou", 409 diz "o que você mandou está bom, mas a
    situação do dado não deixa". Com um None só, a rota não tem como distinguir os
    dois casos.

    O caminho do professor é o mesmo: `SolicitanteInvalido` é 422 porque o dado da
    requisição não serve, e `TarefaConcluida` é 409 porque o dado serve e é a
    situação da tarefa que não deixa.

O que este arquivo **não** tem

    Não tem classe base, não tem `__init__` próprio, não tem atributo, e não tem
    hierarquia: cada uma herda direto de `Exception`, que é o que a aula pede. A
    classe vazia já basta, porque o nome é o motivo e o texto entre parênteses do
    `raise` é a mensagem.

O que também não está aqui

    Não está o "não achou". A tatuagem que não existe não é recusa da regra: é um
    id que não corresponde a nada, e esse continua sendo o `return None` do
    serviço, que a rota traduz em 404. Recusa é a regra dizendo não; não achar é o
    caminho não existindo.
"""

# PassoDesconhecido: o texto enviado no campo tipo não é nenhum dos três passos do
# estúdio. É um problema no dado que chegou, não na situação da tatuagem: se o
# front mandar "agendamento", não há tatuagem, em etapa nenhuma, que possa aceitar
# isso. Por isso o status é 422, o mesmo que o Pydantic usa quando o campo viola
# uma restrição dele.
class PassoDesconhecido(Exception):
    """O tipo enviado não é um passo deste estúdio."""

# EtapaNaoAceitaPasso: o passo é um dos três, mas a tatuagem não está numa etapa
# que ele aceite. Aqui o dado que chegou está perfeito, e quem impede é a situação:
# a cartilha recusa sessão antes do desenho aprovado e retoque antes de pelo menos
# uma sessão. É por isso que o status é 409 e não 422: 422 pediria para o front
# corrigir o campo, e não há nada para corrigar — o Vitor precisa registrar o
# desenho aprovado antes, e a etapa dele sozinha não muda.
class EtapaNaoAceitaPasso(Exception):
    """A tatuagem não está numa etapa que aceite esse passo."""