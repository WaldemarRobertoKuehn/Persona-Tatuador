"""O depósito das contas de usuário, na tabela usuarios.

A conta é a pessoa que entra no sistema, e ela pertence a um grupo que concede
permissões. Este arquivo é só o depósito das contas: ele lê e grava na tabela
usuarios, e nada mais.

Por que a conta não mora mais na tabela clientes

    Antes a conta era uma linha da tabela clientes, com email e senha_hash nela.
    Isso misturava quem é dona de tatuagem e quem tem senha para entrar. Agora
    clientes, tatuadores e administradores têm contas em usuarios; cliente_id
    liga somente a conta Cliente à respectiva linha de clientes.

O que as funções devolvem

    Todas devolvem um dicionário ou None, como antes. Quem consome o depósito
    continua recebendo exatamente o mesmo tipo de coisa, e é por isso que o
    resto do projeto não percebeu a troca da tabela.
"""

# O mesmo banco.py dos outros repositórios: este arquivo não sabe de onde vem a
# conexão, só recebe o cursor pronto.
import banco


# NOVO: o JOIN devolve o código do grupo como papel, preservando o contrato do front.
_CONSULTA_USUARIO = (
    "SELECT u.id, u.nome, u.email, u.usuario, u.senha_hash, u.papel, u.cliente_id, "
    "u.grupo_id, g.codigo AS grupo_codigo, g.nome AS grupo_nome, "
    "COALESCE(("
    "SELECT array_agg(p.codigo ORDER BY p.codigo) "
    "FROM permissoes AS p "
    "JOIN grupos_permissoes AS gp ON gp.permissao_id = p.id "
    "WHERE gp.grupo_id = u.grupo_id"
    "), ARRAY[]::varchar[]) AS permissoes "
    "FROM usuarios AS u LEFT JOIN grupos AS g ON g.id = u.grupo_id "
)


def buscar_por_email(email: str) -> dict | None:
    """Busca uma conta pelo email, sem devolver dados além dos necessários.

    O SELECT pede as colunas pelo nome, e não usa o asterisco. O asterisco
    traria qualquer coluna que alguém acrescentasse na tabela depois, e o
    dicionário devolvido passaria a ter uma chave a mais sem ninguém pedir.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.email = %s",
            (email,),
        )
        return cursor.fetchone()


def buscar_por_usuario(usuario: str) -> dict | None:
    """Busca uma conta pelo identificador curto usado no login."""
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.usuario = %s",
            (usuario,),
        )
        return cursor.fetchone()


def buscar_por_identificador(identificador: str) -> dict | None:
    """Busca pelo e-mail ou pelo usuário, que são os dois jeitos de entrar.

    O e-mail e o usuário têm índices únicos, então a consulta devolve no máximo
    uma linha mesmo com o OR.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.email = %s OR u.usuario = %s",
            (identificador, identificador),
        )
        return cursor.fetchone()


def criar_usuario(
    nome: str,
    email: str,
    senha_hash: str,
    papel: str,
    cliente_id: int | None,
    grupo_id: int,
    usuario: str | None,
) -> dict:
    """Cria a conta e devolve os dados dela, com o id retornado pelo PostgreSQL.

    NOVO: grupo_id grava o vínculo usado para autorizar a conta em cada rota.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO usuarios "
            "(nome, email, senha_hash, papel, cliente_id, grupo_id, usuario) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (nome, email, senha_hash, papel, cliente_id, grupo_id, usuario),
        )
        usuario_id = cursor.fetchone()["id"]
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def atualizar_usuario(usuario_id: int, usuario: str) -> None:
    """Define o identificador curto de uma conta que ainda não tinha um."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET usuario = %s WHERE id = %s",
            (usuario, usuario_id),
        )


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """Busca conta pelo id, incluindo o hash somente para validação interna."""
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def listar_tatuadores() -> list[dict]:
    """Devolve as contas do grupo tatuador, em ordem de nome.

    A consulta usa o mesmo JOIN de permissões das outras buscas, então cada
    conta volta com o grupo e as permissões que valem agora. O hash da senha é
    cortado pela rota, que responde com o esquema público.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO
            + "WHERE g.codigo = 'tatuador' ORDER BY u.nome, u.id"
        )
        return cursor.fetchall()


def buscar_tatuador_por_id(usuario_id: int) -> dict | None:
    """Busca uma conta somente se ela pertencer ao grupo tatuador."""
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO
            + "WHERE g.codigo = 'tatuador' AND u.id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def buscar_tatuador_padrao_id() -> int | None:
    """Devolve o tatuador mais antigo, que é o responsável padrão de um pedido.

    A tatuagem nova nasce com um responsável para a agenda já abrir. Se ainda
    não houver tatuador cadastrado, devolve None e a tatuagem fica sem
    responsável até o administrador atribuir um.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT u.id FROM usuarios AS u "
            "JOIN grupos AS g ON g.id = u.grupo_id "
            "WHERE g.codigo = 'tatuador' ORDER BY u.id LIMIT 1"
        )
        achado = cursor.fetchone()

    return achado["id"] if achado else None


def guardar_token_redefinicao(
    usuario_id: int,
    token_hash: str,
    expira_em,
    solicitado_em,
    limite_anterior,
) -> bool:
    """Grava um token se a conta não solicitou outro durante o intervalo mínimo."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios "
            "SET token_redefinicao_hash = %s, "
            "token_redefinicao_expira_em = %s, "
            "token_redefinicao_solicitado_em = %s "
            "WHERE id = %s AND (token_redefinicao_solicitado_em IS NULL "
            "OR token_redefinicao_solicitado_em <= %s) RETURNING id",
            (token_hash, expira_em, solicitado_em, usuario_id, limite_anterior),
        )
        return cursor.fetchone() is not None


def invalidar_token_redefinicao(token_hash: str) -> None:
    """Invalida somente o token correspondente quando o email não foi enviado."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET token_redefinicao_hash = NULL, "
            "token_redefinicao_expira_em = NULL "
            "WHERE token_redefinicao_hash = %s",
            (token_hash,),
        )


def redefinir_senha_com_token(token_hash: str, senha_hash: str, agora) -> bool:
    """Troca a senha e consome o token numa única operação atômica."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s, token_redefinicao_hash = NULL, "
            "token_redefinicao_expira_em = NULL "
            "WHERE token_redefinicao_hash = %s "
            "AND token_redefinicao_expira_em > %s RETURNING id",
            (senha_hash, token_hash, agora),
        )
        return cursor.fetchone() is not None


def atualizar_senha(usuario_id: int, senha_hash: str) -> None:
    """Atualiza a senha autenticada e invalida qualquer link de redefinição pendente."""
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s, token_redefinicao_hash = NULL, "
            "token_redefinicao_expira_em = NULL WHERE id = %s",
            (senha_hash, usuario_id),
        )
