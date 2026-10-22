"""NOVO: consultas e gravações de grupos e permissões no MySQL."""

import banco


def buscar_grupo_por_codigo(codigo: str) -> dict | None:
    """NOVO: encontra um grupo pelo código estável usado pela aplicação."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, codigo, nome FROM grupos WHERE codigo = %s",
            (codigo,),
        )
        return cursor.fetchone()


def buscar_grupo_por_id(grupo_id: int) -> dict | None:
    """NOVO: encontra um grupo pelo identificador recebido na API."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, codigo, nome FROM grupos WHERE id = %s",
            (grupo_id,),
        )
        return cursor.fetchone()


def buscar_grupo_por_nome(nome: str) -> dict | None:
    """NOVO: detecta nome duplicado antes de criar um grupo."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT id, codigo, nome FROM grupos WHERE nome = %s",
            (nome,),
        )
        return cursor.fetchone()


def contar_administradores() -> int:
    """NOVO: verifica se o bootstrap local ainda precisa criar a conta inicial."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM usuarios AS u "
            "JOIN grupos AS g ON g.id = u.grupo_id "
            "WHERE g.codigo = 'administrador'"
        )
        return cursor.fetchone()["total"]


def listar_grupos() -> list[dict]:
    """NOVO: devolve grupos e códigos de permissões associados."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT g.id, g.codigo, g.nome, p.codigo AS permissao "
            "FROM grupos AS g "
            "LEFT JOIN grupos_permissoes AS gp ON gp.grupo_id = g.id "
            "LEFT JOIN permissoes AS p ON p.id = gp.permissao_id "
            "ORDER BY g.id, p.codigo"
        )
        linhas = cursor.fetchall()

    grupos: dict[int, dict] = {}
    for linha in linhas:
        grupo = grupos.setdefault(
            linha["id"],
            {
                "id": linha["id"],
                "codigo": linha["codigo"],
                "nome": linha["nome"],
                "permissoes": [],
            },
        )
        if linha["permissao"] is not None:
            grupo["permissoes"].append(linha["permissao"])
    return list(grupos.values())


def criar_grupo(codigo: str, nome: str, permissoes: list[str]) -> dict:
    """NOVO: grava grupo e vínculos de permissão na mesma transação."""
    with banco.cursor() as cursor:
        cursor.execute(
            "INSERT INTO grupos (codigo, nome) VALUES (%s, %s)",
            (codigo, nome),
        )
        grupo_id = cursor.lastrowid
        for permissao in permissoes:
            cursor.execute(
                "INSERT INTO grupos_permissoes (grupo_id, permissao_id) "
                "SELECT %s, id FROM permissoes WHERE codigo = %s",
                (grupo_id, permissao),
            )
    return {
        "id": grupo_id,
        "codigo": codigo,
        "nome": nome,
        "permissoes": sorted(permissoes),
    }


def substituir_permissoes(grupo_id: int, permissoes: list[str]) -> None:
    """NOVO: substitui a lista de permissões do grupo atomicamente."""
    with banco.cursor() as cursor:
        cursor.execute(
            "DELETE FROM grupos_permissoes WHERE grupo_id = %s",
            (grupo_id,),
        )
        for permissao in permissoes:
            cursor.execute(
                "INSERT INTO grupos_permissoes (grupo_id, permissao_id) "
                "SELECT %s, id FROM permissoes WHERE codigo = %s",
                (grupo_id, permissao),
            )


def atribuir_usuario_ao_grupo(usuario_id: int, grupo: dict) -> str:
    """NOVO: altera grupo atomicamente e preserva ao menos um Administrador."""
    with banco.cursor() as cursor:
        # NOVO: serializa alterações de grupo usando a linha fixa do grupo admin.
        cursor.execute(
            "SELECT id FROM grupos WHERE codigo = 'administrador' FOR UPDATE"
        )
        cursor.fetchone()
        cursor.execute(
            "SELECT u.grupo_id, u.nome, u.cliente_id, g.codigo "
            "FROM usuarios AS u "
            "JOIN grupos AS g ON g.id = u.grupo_id "
            "WHERE u.id = %s FOR UPDATE",
            (usuario_id,),
        )
        usuario = cursor.fetchone()
        if usuario is None:
            return "usuario_inexistente"
        if usuario["codigo"] == "administrador" and grupo["codigo"] != "administrador":
            cursor.execute(
                "SELECT COUNT(*) AS total FROM usuarios AS u "
                "JOIN grupos AS g ON g.id = u.grupo_id "
                "WHERE g.codigo = 'administrador'"
            )
            if cursor.fetchone()["total"] <= 1:
                return "ultimo_administrador"
        cliente_id = usuario["cliente_id"]
        if grupo["codigo"] == "cliente" and cliente_id is None:
            # NOVO: contas promovidas a Cliente precisam de um registro de dono
            # para que o escopo de tatuagens próprias funcione.
            cursor.execute(
                "INSERT INTO clientes (nome) VALUES (%s)",
                (usuario["nome"],),
            )
            cliente_id = cursor.lastrowid
        cursor.execute(
            "UPDATE usuarios SET grupo_id = %s, papel = %s, cliente_id = %s "
            "WHERE id = %s",
            (grupo["id"], grupo["codigo"], cliente_id, usuario_id),
        )
        return "atualizado"


def listar_permissoes_do_usuario(usuario_id: int) -> list[str]:
    """NOVO: lê permissões atuais, sem confiar em dados de papel do token."""
    with banco.cursor() as cursor:
        cursor.execute(
            "SELECT p.codigo FROM permissoes AS p "
            "JOIN grupos_permissoes AS gp ON gp.permissao_id = p.id "
            "JOIN usuarios AS u ON u.grupo_id = gp.grupo_id "
            "WHERE u.id = %s ORDER BY p.codigo",
            (usuario_id,),
        )
        return [linha["codigo"] for linha in cursor.fetchall()]
