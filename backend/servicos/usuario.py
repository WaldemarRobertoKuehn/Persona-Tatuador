"""Regras de cadastro, busca e validação de contas de usuário."""

import repositorios.cliente as repositorio_clientes
import repositorios.usuario as repositorio_usuarios
import seguranca

# Os dois papéis que existem no sistema. O papel é a decisão que muda o que a
# pessoa vê depois de entrar, e ele fica no banco, e não na tela.
PAPEL_CLIENTE = "cliente"
PAPEL_TATUADOR = "tatuador"


def cadastrar(dados: dict) -> dict | None:
    """Cria uma conta ou devolve None quando o email já está cadastrado.

    Quem se cadastra pelo formulário público entra como cliente, porque quem
    pede tatuagem no estúdio é cliente. O papel "tatuador" é do dono e dos
    tatuadores do estúdio, e quem cria essa conta é o próprio estúdio, não a
    tela de cadastro.

    A conta de papel "cliente" fica ligada a uma linha da tabela clientes, e é
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
    cliente_id = dados.get("cliente_id")

    if papel == PAPEL_CLIENTE and cliente_id is None:
        cliente_id = repositorio_clientes.criar_cliente(nome)

    try:
        return repositorio_usuarios.criar_usuario(
            nome, email, senha_hash, papel, cliente_id
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


def buscar_por_id(usuario_id: int) -> dict | None:
    return repositorio_usuarios.buscar_usuario_por_id(usuario_id)


def trocar_senha(email: str, senha_nova: str) -> bool:
    """Troca a senha da conta, e devolve False se a conta não existir.

    A senha nova nunca é gravada: o que vai para o banco é o hash novo, e o
    hash antigo morre junto com ele. É o mesmo caminho do cadastro, e por isso
    a senha da conta nunca fica em texto em lugar nenhum.
    """
    usuario = repositorio_usuarios.buscar_por_email(email.strip().lower())

    if usuario is None:
        return False

    repositorio_usuarios.atualizar_senha(
        usuario["id"], seguranca.gerar_hash(senha_nova)
    )
    return True


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

    conta = repositorio_usuarios.criar_usuario(
        acesso["nome"],
        acesso["email"],
        acesso["senha_hash"],
        papel,
        cliente_id if papel == PAPEL_CLIENTE else None,
    )
    repositorio_clientes.esvaziar_acesso(cliente_id)

    return conta
