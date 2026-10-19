"""O depósito das contas de usuário, na mesma tabela clientes.

O usuário do sistema é a pessoa da tabela clientes, e este arquivo é o depósito
só das funções de conta: cadastro, busca pelo email e busca pelo id. A busca da
cliente para mostrar o nome na tatuagem continua em repositorios/cliente.py,
porque é outro uso do mesmo registro: um lado é a conta que entra no sistema, e
o outro é a pessoa que assinou a tatuagem.
"""

# O mesmo banco.py dos outros repositórios: este arquivo não sabe de onde vem a
# conexão, só recebe o cursor pronto.
import banco


def buscar_por_email(email: str) -> dict | None:
    """Busca uma conta pelo email, sem devolver dados além dos necessários."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE email = %s",
            (email,),
        )
        return cursor.fetchone()


def criar_usuario(nome: str, email: str, senha_hash: str) -> dict:
    """Cria a conta e devolve seus dados públicos e o hash para uso interno."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO clientes (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, senha_hash),
        )
        usuario_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """Busca conta por id, incluindo o hash somente para validação interna."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, nome, email, senha_hash FROM clientes WHERE id = %s",
            (usuario_id,),
        )
        return cursor.fetchone()
