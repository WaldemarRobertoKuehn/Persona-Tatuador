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


# AprovaçãoDoClienteNecessaria: o tatuador tentou registrar "desenho aprovado"
# pelo formulário de passos. A etapa só anda quando o cliente aprova uma imagem de
# desenho, então o serviço recusa o atalho.
class AprovacaoDoClienteNecessaria(Exception):
    """O desenho só pode ser aprovado pelo cliente, na imagem enviada."""


# TipoDeImagemDesconhecido: o tipo enviado não é desenho nem referência.
class TipoDeImagemDesconhecido(Exception):
    """O tipo de imagem enviado não é aceito."""


# ImagemNaoEncontrada: o id da imagem não pertence à tatuagem consultada.
class ImagemNaoEncontrada(Exception):
    """A imagem não existe nesta tatuagem."""


# ArquivoDeImagemInvalido: o arquivo está vazio, é grande demais ou não é uma
# imagem de um formato permitido.
class ArquivoDeImagemInvalido(Exception):
    """O arquivo enviado não serve como imagem."""


# ImagemNaoAprovavel: o cliente tentou aprovar uma referência, e não o desenho.
class ImagemNaoAprovavel(Exception):
    """Só uma imagem do tipo desenho pode ser aprovada."""


# ImagemJaAprovada: o cliente tentou recusar uma imagem que já aprovou.
class ImagemJaAprovada(Exception):
    """A imagem já foi aprovada e não pode ser recusada."""


# AgendamentoNaoEncontrado: o id não pertence à tatuagem consultada.
class AgendamentoNaoEncontrado(Exception):
    """O agendamento não existe nesta tatuagem."""


# AgendamentoJaCancelado: o tatuador tentou cancelar duas vezes o mesmo horário.
class AgendamentoJaCancelado(Exception):
    """O agendamento já está cancelado."""


# TipoDeAgendamentoDesconhecido: o texto não é "sessão" nem "retoque".
class TipoDeAgendamentoDesconhecido(Exception):
    """O tipo de agendamento enviado não é aceito."""


# EtapaNaoPermiteAgendamento: a tatuagem ainda está esperando o desenho ou já
# foi finalizada, então não há o que agendar.
class EtapaNaoPermiteAgendamento(Exception):
    """A etapa atual da tatuagem não permite agendamento."""


# TatuagemSemTatuador: a tatuagem ainda não tem um profissional responsável,
# então não existe agenda para consultar ou marcar. É diferente de dia fechado:
# o expediente existe, mas falta a agenda de quem atende.
class TatuagemSemTatuador(Exception):
    """A tatuagem ainda não tem tatuador responsável."""


# AgendamentoConflitante: ao trocar o tatuador responsável, um dos horários já
# marcados desta tatuagem colide com a agenda do profissional novo.
class AgendamentoConflitante(Exception):
    """O tatuador novo já atende em um dos horários marcados da tatuagem."""


# DataForaDoExpediente: o dia escolhido é domingo ou não tem horário de
# atendimento.
class DataForaDoExpediente(Exception):
    """O estúdio não atende nesse dia."""


# HorarioForaDoExpediente: a hora escolhida não é o começo de um bloco de uma
# hora do expediente.
class HorarioForaDoExpediente(Exception):
    """O horário escolhido não faz parte do expediente."""


# AgendamentoNoPassado: o horário já começou ou já passou.
class AgendamentoNoPassado(Exception):
    """Não é possível agendar um horário que já passou."""


# HorarioIndisponivel: o tatuador já tem outro agendamento ativo nesse horário.
class HorarioIndisponivel(Exception):
    """O tatuador já está ocupado nesse horário."""


# AgendamentoDeOutroTatuador: o tatuador tentou cancelar um horário que pertence
# à agenda de outra pessoa.
class AgendamentoDeOutroTatuador(Exception):
    """O agendamento pertence à agenda de outro tatuador."""