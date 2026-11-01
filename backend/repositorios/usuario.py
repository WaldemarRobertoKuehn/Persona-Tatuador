"""O depósito das contas de usuário, na tabela usuarios.

A conta é a pessoa que entra no sistema, e ela pertence a um grupo que concede
permissões. Este arquivo é só o depósito das contas: ele lê e grava na tabela
usuarios, e nada mais.

Por que a conta não mora mais na tabela clientes

    Antes a conta era uma linha da tabela clientes, com email e senha_hash nela.
    Isso misturava duas coisas do negócio: quem é dona de tatuagem e quem tem
    senha para entrar. O tatuador é dono do estúdio e não é dona de nenhuma
    tatuagem, e mesmo assim precisava de uma linha em clientes só para ter
    login. Agora a conta mora na tabela usuarios, e a coluna cliente_id é o elo
    com a cliente da cartilha: ele é preenchido só para o papel "cliente".

O que as funções devolvem

    Todas devolvem um dicionário ou None, como antes. Quem consome o depósito
    continua recebendo exatamente o mesmo tipo de coisa, e é por isso que o
    resto do projeto não percebeu a troca da tabela.
"""

from datetime import datetime, timedelta, timezone

# O mesmo banco.py dos outros repositórios: este arquivo não sabe de onde vem a
# conexão, só recebe o cursor pronto.
import banco


# NOVO: o JOIN devolve o código do grupo como papel, preservando o contrato do front.
_CONSULTA_USUARIO = (
    "SELECT u.id, u.nome, u.email, u.senha_hash, u.papel, u.cliente_id, "
    "u.grupo_id, g.codigo AS grupo_codigo, g.nome AS grupo_nome "
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


def criar_usuario(
    nome: str,
    email: str,
    senha_hash: str,
    papel: str,
    cliente_id: int | None,
    grupo_id: int,
) -> dict:
    """Cria a conta e devolve os dados dela, com o id retornado pelo PostgreSQL.

    NOVO: grupo_id grava o vínculo usado para autorizar a conta em cada rota.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, papel, cliente_id, grupo_id) "
            "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (nome, email, senha_hash, papel, cliente_id, grupo_id),
        )
        usuario_id = cursor.fetchone()["id"]
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """Busca conta pelo id, incluindo o hash somente para validação interna."""
    with banco.cursor() as cursor:
        cursor.execute(
            _CONSULTA_USUARIO + "WHERE u.id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def atualizar_senha(usuario_id: int, senha_hash: str) -> None:
    """Troca o hash da senha da conta.

    O que entra na coluna senha_hash é sempre o hash novo, e nunca a senha em
    texto: quem calcula o hash é o serviço, e o repositório só grava.
    """
    with banco.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
            (senha_hash, usuario_id),
        )
        cursor.execute(
            "DELETE FROM tokens_redefinicao_senha WHERE usuario_id = %s",
            (usuario_id,),
        )


def criar_token_redefinicao(
    usuario_id: int,
    token_hash: str,
    criado_em: datetime,
    expira_em: datetime,
) -> bool:
    """Registra um token e limita cada conta a uma solicitação por minuto."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id FROM usuarios WHERE id = %s FOR UPDATE",
            (usuario_id,),
        )
        if cursor.fetchone() is None:
            return False

        cursor.execute(
            "SELECT criado_em FROM tokens_redefinicao_senha "
            "WHERE usuario_id = %s FOR UPDATE",
            (usuario_id,),
        )
        token_existente = cursor.fetchone()
        if token_existente is not None:
            ultima_solicitacao = token_existente["criado_em"]
            if ultima_solicitacao.tzinfo is None:
                ultima_solicitacao = ultima_solicitacao.replace(tzinfo=timezone.utc)
            if criado_em - ultima_solicitacao < timedelta(minutes=1):
                return False

            cursor.execute(
                "DELETE FROM tokens_redefinicao_senha WHERE usuario_id = %s",
                (usuario_id,),
            )

        cursor.execute(
            "INSERT INTO tokens_redefinicao_senha "
            "(usuario_id, token_hash, criado_em, expira_em) "
            "VALUES (%s, %s, %s, %s)",
            (usuario_id, token_hash, criado_em, expira_em),
        )
        return True


def remover_token_redefinicao(token_hash: str) -> None:
    """Remove o token quando o envio do e-mail falha."""
    with banco.cursor() as cursor:
        cursor.execute(
            "DELETE FROM tokens_redefinicao_senha WHERE token_hash = %s",
            (token_hash,),
        )


def token_redefinicao_valido(token_hash: str) -> bool:
    """Confere a existência e a validade sem calcular um hash de senha."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT expira_em FROM tokens_redefinicao_senha WHERE token_hash = %s",
            (token_hash,),
        )
        token = cursor.fetchone()
        if token is None:
            return False

        expiracao = token["expira_em"]
        if expiracao.tzinfo is None:
            expiracao = expiracao.replace(tzinfo=timezone.utc)
        return expiracao > datetime.now(timezone.utc)


def consumir_token_redefinicao(token_hash: str, senha_hash: str) -> bool:
    """Troca a senha e invalida o token na mesma transação."""
    agora = datetime.now(timezone.utc)
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT usuario_id, expira_em FROM tokens_redefinicao_senha "
            "WHERE token_hash = %s FOR UPDATE",
            (token_hash,),
        )
        token = cursor.fetchone()
        if token is None:
            return False

        expiracao = token["expira_em"]
        if expiracao.tzinfo is None:
            expiracao = expiracao.replace(tzinfo=timezone.utc)
        if expiracao <= agora:
            cursor.execute(
                "DELETE FROM tokens_redefinicao_senha WHERE token_hash = %s",
                (token_hash,),
            )
            return False

        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
            (senha_hash, token["usuario_id"]),
        )
        cursor.execute(
            "DELETE FROM tokens_redefinicao_senha WHERE usuario_id = %s",
            (token["usuario_id"],),
        )
        return True
