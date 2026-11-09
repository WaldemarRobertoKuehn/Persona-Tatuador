"""Regras de cadastro, busca e validação de contas de usuário."""

from datetime import datetime, timedelta, timezone
import hashlib
import logging
import secrets

import configuracao
import repositorios.cliente as repositorio_clientes
import repositorios.grupo as repositorio_grupos
import repositorios.usuario as repositorio_usuarios
import seguranca
import servicos.email as servico_email
import validacao_email

# Os códigos iniciais dos dois grupos de persona. A permissão efetiva vem agora
# do vínculo de grupo e do catálogo administrável, não apenas destes códigos.
PAPEL_CLIENTE = "cliente"
PAPEL_TATUADOR = "tatuador"
logger = logging.getLogger(__name__)


def cadastrar(dados: dict, *, validar_email: bool = True) -> dict | None:
    """Cria uma conta ou devolve None quando o email já está cadastrado.

    Quem se cadastra pelo formulário público entra no grupo cliente. Os outros
    grupos são atribuídos pelo Administrador ou por scripts locais confiáveis.

    A conta do grupo "cliente" fica ligada a uma linha da tabela clientes, e é
    essa ligação que faz "minhas tatuagens" filtrar por cliente_id. Quando a
    pessoa ainda não é cliente do estúdio, o serviço cria a linha dela aqui, em
    um commit só: ou os dois nascem, ou nenhum dos dois nasce.

    A checagem do e-mail acontece antes de qualquer gravação. Se o endereço não
    puder receber a confirmação, EmailInvalidoError sobe e nenhuma linha é
    criada, nem em clientes nem em usuarios. Scripts de demonstração que usam
    endereços internos passam validar_email=False.

    O usuário curto é escolhido por quem se cadastra e chega em dados["usuario"].
    Contas antigas que ainda não têm um passam por definir_usuario().
    """
    email = dados["email"].strip().lower()
    if repositorio_usuarios.buscar_por_email(email) is not None:
        return None
    usuario_login = dados["usuario"].strip().lower()
    if repositorio_usuarios.buscar_por_usuario(usuario_login) is not None:
        return None
    if validar_email:
        validacao_email.validar_email_entregavel(email)
    senha_hash = seguranca.gerar_hash(dados["senha"])
    nome = dados["nome"].strip()
    papel = dados.get("papel", PAPEL_CLIENTE)
    # NOVO: cada usuário é vinculado a um grupo existente, nunca a permissões
    # enviadas pela tela de cadastro.
    grupo = repositorio_grupos.buscar_grupo_por_codigo(papel)
    if grupo is None:
        raise ValueError("O grupo informado não existe.")
    cliente_id = dados.get("cliente_id")

    if grupo["codigo"] == PAPEL_CLIENTE and cliente_id is None:
        cliente_id = repositorio_clientes.criar_cliente(nome)
    if grupo["codigo"] != PAPEL_CLIENTE:
        cliente_id = None

    try:
        usuario = repositorio_usuarios.criar_usuario(
            nome,
            email,
            senha_hash,
            grupo["codigo"],
            cliente_id,
            grupo["id"],
            usuario_login,
        )
    except Exception as erro:
        # Trata a corrida em que duas requisições tentam cadastrar o mesmo email.
        if getattr(erro, "errno", None) == 1062:
            return None
        raise

    # A confirmação de cadastro vale para qualquer grupo (cliente, tatuador ou
    # administrador) e usa o email da própria conta. Uma falha no envio nunca
    # desfaz a conta, que já está gravada.
    _notificar_conta_criada(usuario)
    return usuario


def cadastrar_tatuador(dados: dict) -> dict | None:
    """Cria uma conta no grupo tatuador; quem chama já passou pela permissão.

    O papel não vem do corpo da requisição: ele é fixado aqui, para a rota
    administrativa não poder criar administrador por engano.
    """
    return cadastrar({**dados, "papel": PAPEL_TATUADOR})


def listar_tatuadores() -> list[dict]:
    """Devolve as contas do grupo tatuador para a tela de administração."""
    return repositorio_usuarios.listar_tatuadores()


def _notificar_conta_criada(usuario: dict) -> None:
    """Envia a confirmação de cadastro sem interromper a criação da conta."""
    if not usuario.get("email") or configuracao.configuracao_smtp() is None:
        return
    try:
        servico_email.enviar_boas_vindas(
            usuario["email"],
            usuario["nome"],
            usuario["usuario"],
            f"{configuracao.endereco_do_front()}/",
        )
    except Exception:
        logger.exception("Falha ao enviar email de confirmação de cadastro.")


def autenticar(identificador: str, senha: str) -> dict | None:
    """Devolve a conta quando o e-mail ou o usuário curto e a senha conferem."""
    identificador = identificador.strip().lower()
    usuario = repositorio_usuarios.buscar_por_identificador(identificador)
    if usuario is None or not usuario.get("senha_hash"):
        return None
    if not seguranca.verificar_senha(senha, usuario["senha_hash"]):
        return None
    return usuario


def definir_usuario(usuario_id: int, usuario: str) -> bool:
    """Define ou troca o usuário curto, recusando um que já é de outra conta."""
    usuario = usuario.strip().lower()
    existente = repositorio_usuarios.buscar_por_usuario(usuario)
    if existente is not None and existente["id"] != usuario_id:
        return False
    repositorio_usuarios.atualizar_usuario(usuario_id, usuario)
    return True


def solicitar_redefinicao_senha(email: str) -> None:
    """Envia um link temporário sem revelar se existe uma conta para o email."""
    usuario = repositorio_usuarios.buscar_por_email(email.strip().lower())
    if usuario is None:
        return

    agora = datetime.now(timezone.utc)
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    limite_anterior = agora - timedelta(seconds=60)
    foi_gravado = repositorio_usuarios.guardar_token_redefinicao(
        usuario["id"],
        token_hash,
        agora + timedelta(minutes=15),
        agora,
        limite_anterior,
    )
    if not foi_gravado:
        return

    link = f"{configuracao.endereco_do_front()}/#redefinir-senha={token}"
    try:
        servico_email.enviar_link_redefinicao(usuario["email"], usuario["nome"], link)
    except Exception:
        repositorio_usuarios.invalidar_token_redefinicao(token_hash)
        logger.exception("Falha ao enviar email de redefinição de senha.")


def redefinir_senha(token: str, senha: str) -> bool:
    """Valida e consome o token de email ao salvar a senha nova."""
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return repositorio_usuarios.redefinir_senha_com_token(
        token_hash,
        seguranca.gerar_hash(senha),
        datetime.now(timezone.utc),
    )


def alterar_senha(usuario_id: int, senha_atual: str, senha_nova: str) -> bool:
    """Exige a senha atual antes de atualizar a senha da sessão autenticada."""
    usuario = repositorio_usuarios.buscar_usuario_por_id(usuario_id)
    if usuario is None or not seguranca.verificar_senha(
        senha_atual, usuario["senha_hash"]
    ):
        return False
    repositorio_usuarios.atualizar_senha(usuario_id, seguranca.gerar_hash(senha_nova))
    return True


def buscar_por_id(usuario_id: int) -> dict | None:
    # As permissões vêm na mesma consulta do usuário, para que uma alteração
    # administrativa continue tendo efeito imediato sem abrir outra conexão.
    return repositorio_usuarios.buscar_usuario_por_id(usuario_id)


def mover_conta(cliente_id: int, papel: str) -> dict | None:
    """Leva para a tabela usuarios a conta que ainda estava na tabela clientes.

    Esta função existe para o momento da mudança: a conta do dono do estúdio
    foi criada quando o login morava na tabela clientes, e a senha dela é um
    hash que já está pronto. Copiar o hash para a tabela usuarios é o jeito de
    mudar de mesa sem trocar a senha: a pessoa continua entrando com a mesma.

    O hash é copiado, nunca decifrado, e as colunas velhas são esvaziadas em
    seguida, para o mesmo email não ficar escrito em dois lugares.
    """
    acesso = repositorio_clientes.buscar_acesso(cliente_id)

    if acesso is None or not acesso.get("email") or not acesso.get("senha_hash"):
        return None

    if repositorio_usuarios.buscar_por_email(acesso["email"]) is not None:
        return None

    grupo = repositorio_grupos.buscar_grupo_por_codigo(papel)
    if grupo is None:
        raise ValueError("O grupo informado não existe.")
    # A conta antiga entra sem usuário curto e define um depois, pela tela.
    conta = repositorio_usuarios.criar_usuario(
        acesso["nome"],
        acesso["email"],
        acesso["senha_hash"],
        grupo["codigo"],
        cliente_id if papel == PAPEL_CLIENTE else None,
        grupo["id"],
        None,
    )
    repositorio_clientes.esvaziar_acesso(cliente_id)

    return conta
