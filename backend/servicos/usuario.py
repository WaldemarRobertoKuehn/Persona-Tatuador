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

# Os códigos iniciais dos dois grupos de persona. A permissão efetiva vem agora
# do vínculo de grupo e do catálogo administrável, não apenas destes códigos.
PAPEL_CLIENTE = "cliente"
PAPEL_TATUADOR = "tatuador"
logger = logging.getLogger(__name__)


def cadastrar(dados: dict) -> dict | None:
    """Cria uma conta ou devolve None quando o email já está cadastrado.

    Quem se cadastra pelo formulário público entra no grupo cliente. Os outros
    grupos são atribuídos pelo Administrador ou por scripts locais confiáveis.

    A conta do grupo "cliente" fica ligada a uma linha da tabela clientes, e é
    essa ligação que faz "minhas tatuagens" filtrar por cliente_id. Quando a
    pessoa ainda não é cliente do estúdio, o serviço cria a linha dela aqui, em
    um commit só: ou os dois nascem, ou nenhum dos dois nasce.
    """
    email = dados["email"].strip().lower()
    if repositorio_usuarios.buscar_por_email(email) is not None:
        return None
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
        return repositorio_usuarios.criar_usuario(
            nome, email, senha_hash, grupo["codigo"], cliente_id, grupo["id"]
        )
    except Exception as erro:
        # Trata a corrida em que duas requisições tentam cadastrar o mesmo email.
        if getattr(erro, "errno", None) == 1062:
            return None
        raise


def autenticar(email: str, senha: str) -> dict | None:
    """Devolve a conta quando o email e a senha conferem."""
    usuario = repositorio_usuarios.buscar_por_email(email.strip().lower())
    if usuario is None or not usuario.get("senha_hash"):
        return None
    if not seguranca.verificar_senha(senha, usuario["senha_hash"]):
        return None
    return usuario


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
    # NOVO: a migração provisiona os grupos de persona; a conta antiga passa a
    # carregar também o identificador do grupo correspondente.
    conta = repositorio_usuarios.criar_usuario(
        acesso["nome"],
        acesso["email"],
        acesso["senha_hash"],
        grupo["codigo"],
        cliente_id if papel == PAPEL_CLIENTE else None,
        grupo["id"],
    )
    repositorio_clientes.esvaziar_acesso(cliente_id)

    return conta
