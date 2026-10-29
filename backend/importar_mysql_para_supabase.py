"""Importa os dados do MySQL legado para o PostgreSQL do Supabase.

O script lê o MySQL antigo sem alterar nada e grava no banco configurado em
backend/.env. Sem --executar ele apenas simula a transação e desfaz tudo no final.

Uso:
    python importar_mysql_para_supabase.py --listar
    python importar_mysql_para_supabase.py
    python importar_mysql_para_supabase.py --executar --limpar
"""

import argparse
import os
import re
import sys
from datetime import date, datetime
from decimal import Decimal
from getpass import getpass
from pathlib import Path

BASE = Path(__file__).resolve().parent
os.chdir(BASE)
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from dotenv import load_dotenv

load_dotenv(BASE / ".env.migracao")
load_dotenv(BASE / ".env", override=False)

import psycopg2
import pymysql
from psycopg2 import sql
from psycopg2.extras import RealDictCursor, execute_values

import configuracao

TABELAS_DADOS = ("clientes", "usuarios", "tatuagens", "passos")
TABELAS_ORIGEM = ("clientes", "usuarios", "tatuagens", "passos", "grupos")
ORDEM_DE_INSERCAO = ("clientes", "usuarios", "tatuagens", "passos")
GRUPOS_OBRIGATORIOS = ("cliente", "tatuador", "administrador")
IDENTIFICADOR = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa os dados do MySQL legado para o PostgreSQL do Supabase."
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MYSQL_HOST", "127.0.0.1"),
        help="Host do MySQL (padrão: MYSQL_HOST ou 127.0.0.1).",
    )
    parser.add_argument(
        "--porta",
        type=int,
        default=int(os.getenv("MYSQL_PORT", os.getenv("MYSQL_PORTA", "3306"))),
        help="Porta do MySQL (padrão: MYSQL_PORT ou 3306).",
    )
    parser.add_argument(
        "--usuario",
        default=os.getenv("MYSQL_USER", os.getenv("MYSQL_USUARIO", "root")),
        help="Usuário do MySQL (padrão: MYSQL_USER ou root).",
    )
    parser.add_argument(
        "--banco",
        default=os.getenv("MYSQL_DATABASE", os.getenv("MYSQL_BANCO", "traco_fino")),
        help="Banco do MySQL (padrão: MYSQL_DATABASE ou traco_fino).",
    )
    parser.add_argument(
        "--listar",
        action="store_true",
        help="Mostra tabelas, colunas e contagens, sem importar.",
    )
    parser.add_argument(
        "--executar",
        action="store_true",
        help="Grava de verdade. Sem esta opção, a transação é desfeita no final.",
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Apaga clientes, usuários, tatuagens e passos do Supabase antes de importar.",
    )
    parser.add_argument(
        "--ignorar-orfaos",
        action="store_true",
        help="Ignora tatuagens/passos cuja referência não existe na origem.",
    )
    parser.add_argument(
        "--conta-tatuador",
        action="append",
        default=[],
        metavar="EMAIL",
        help="E-mail de conta antiga em clientes que deve virar tatuador (pode repetir).",
    )
    parser.add_argument(
        "--conta-administrador",
        action="append",
        default=[],
        metavar="EMAIL",
        help="E-mail de conta antiga em clientes que deve virar administrador (pode repetir).",
    )
    parser.add_argument(
        "--sem-contas",
        action="store_true",
        help="Não cria contas em usuarios; copia clientes como estão.",
    )
    args = parser.parse_args()
    if args.limpar and not args.executar:
        parser.error("--limpar só pode ser usado junto com --executar.")
    return args


def senha_mysql() -> str:
    senha = os.getenv("MYSQL_PASSWORD")
    if senha is None:
        senha = os.getenv("MYSQL_SENHA")
    if senha is not None:
        return senha
    if not sys.stdin.isatty():
        raise SystemExit(
            "Defina MYSQL_PASSWORD no backend/.env.migracao ou execute em um terminal."
        )
    return getpass("Senha do MySQL: ")


def conectar_mysql(args: argparse.Namespace):
    return pymysql.connect(
        host=args.host,
        port=args.porta,
        user=args.usuario,
        password=senha_mysql(),
        database=args.banco,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
        read_timeout=60,
        write_timeout=60,
        autocommit=True,
    )


def conectar_postgres():
    endereco = configuracao.endereco_do_banco()
    return psycopg2.connect(
        host=endereco.host,
        port=endereco.port,
        user=endereco.username,
        password=endereco.password,
        dbname=endereco.database,
        sslmode=endereco.query.get("sslmode", "require"),
        connect_timeout=10,
    )


def identificador_mysql(nome: str) -> str:
    if not IDENTIFICADOR.fullmatch(nome):
        raise ValueError(f"Identificador MySQL inesperado: {nome}")
    return f"`{nome}`"


def listar_tabelas_mysql(cursor) -> dict[str, str]:
    cursor.execute(
        "SELECT TABLE_NAME AS nome FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE' "
        "ORDER BY TABLE_NAME"
    )
    return {linha["nome"].lower(): linha["nome"] for linha in cursor.fetchall()}


def colunas_mysql(cursor, tabela: str) -> list[dict]:
    cursor.execute(
        "SELECT COLUMN_NAME AS nome, DATA_TYPE AS tipo, IS_NULLABLE AS permite_nulo, "
        "COLUMN_KEY AS chave, COLUMN_DEFAULT AS padrao "
        "FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION",
        (tabela,),
    )
    return cursor.fetchall()


def contar_mysql(cursor, tabela: str) -> int:
    cursor.execute(f"SELECT COUNT(*) AS total FROM {identificador_mysql(tabela)}")
    return int(cursor.fetchone()["total"])


def colunas_postgres(cursor, tabela: str) -> list[dict]:
    cursor.execute(
        "SELECT column_name AS nome, data_type AS tipo, is_nullable AS permite_nulo, "
        "column_default AS padrao "
        "FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = %s "
        "ORDER BY ordinal_position",
        (tabela,),
    )
    return cursor.fetchall()


def carregar_dados(cursor, tabelas: dict[str, str]) -> dict[str, list[dict]]:
    dados = {}
    for nome in TABELAS_ORIGEM:
        tabela_real = tabelas.get(nome)
        if tabela_real is None:
            continue
        cursor.execute(f"SELECT * FROM {identificador_mysql(tabela_real)}")
        dados[nome] = [dict(linha) for linha in cursor.fetchall()]
    return dados


def carregar_grupos(cursor) -> dict[str, int]:
    cursor.execute("SELECT id, codigo FROM grupos ORDER BY id")
    grupos = {linha["codigo"]: linha["id"] for linha in cursor.fetchall()}
    faltando = sorted(set(GRUPOS_OBRIGATORIOS) - set(grupos))
    if faltando:
        raise SystemExit(
            "Grupos ausentes no Supabase: " + ", ".join(faltando)
            + ". Rode as migrations antes de importar."
        )
    return grupos


def proximo_id_usuarios(cursor, dados: dict[str, list[dict]]) -> int:
    cursor.execute("SELECT COALESCE(MAX(id), 0) AS maior FROM usuarios")
    maior_supabase = int(cursor.fetchone()["maior"])
    maior_origem = max(
        (int(linha.get("id") or 0) for linha in dados.get("usuarios", [])),
        default=0,
    )
    return max(maior_supabase, maior_origem) + 1


def montar_dados(
    dados: dict[str, list[dict]],
    grupos: dict[str, int],
    args: argparse.Namespace,
    proximo_id: int,
) -> tuple[dict[str, list[dict]], list[str]]:
    avisos = []
    clientes = [dict(linha) for linha in dados.get("clientes", [])]
    usuarios = []

    mapa_grupos_origem = {}
    for grupo in dados.get("grupos", []):
        codigo = (grupo.get("codigo") or "").strip().lower()
        if codigo in grupos:
            mapa_grupos_origem[grupo.get("id")] = codigo

    emails_origem = set()
    for linha in dados.get("usuarios", []):
        usuario = dict(linha)
        codigo = (usuario.get("papel") or "").strip().lower()
        if codigo not in grupos:
            codigo = mapa_grupos_origem.get(usuario.get("grupo_id"), "")
        if codigo not in grupos:
            avisos.append(
                f"Usuário {usuario.get('id')} sem grupo reconhecido; usando cliente."
            )
            codigo = "cliente"
        if not usuario.get("email") or not usuario.get("senha_hash"):
            avisos.append(
                f"Usuário {usuario.get('id')} sem email ou hash; não será importado."
            )
            continue
        usuario["email"] = str(usuario["email"]).strip().lower()
        if usuario["email"] in emails_origem:
            avisos.append(
                f"Usuário {usuario.get('id')} repetiu o email de outra conta; "
                "não será importado."
            )
            continue
        emails_origem.add(usuario["email"])
        usuario["papel"] = codigo
        usuario["grupo_id"] = grupos[codigo]
        if codigo != "cliente":
            usuario["cliente_id"] = None
        usuarios.append(usuario)

    if not args.sem_contas:
        emails_usuarios = {usuario["email"] for usuario in usuarios}
        emails_tatuador = {email.strip().lower() for email in args.conta_tatuador}
        emails_administrador = {
            email.strip().lower() for email in args.conta_administrador
        }

        for cliente in clientes:
            email = cliente.get("email")
            senha_hash = cliente.get("senha_hash")
            if not email or not senha_hash:
                continue
            email = str(email).strip().lower()
            if email in emails_usuarios:
                cliente["email"] = None
                cliente["senha_hash"] = None
                continue
            codigo = (cliente.get("papel") or "").strip().lower()
            if email in emails_administrador:
                codigo = "administrador"
            elif email in emails_tatuador:
                codigo = "tatuador"
            elif codigo not in grupos:
                codigo = "cliente"
            usuario = {
                "id": proximo_id,
                "nome": cliente.get("nome") or email,
                "email": email,
                "senha_hash": senha_hash,
                "papel": codigo,
                "grupo_id": grupos[codigo],
                "cliente_id": cliente.get("id") if codigo == "cliente" else None,
            }
            proximo_id += 1
            usuarios.append(usuario)
            emails_usuarios.add(email)
            cliente["email"] = None
            cliente["senha_hash"] = None

    if args.sem_contas:
        usuarios = []

    return {
        "clientes": clientes,
        "usuarios": usuarios,
        "tatuagens": [dict(linha) for linha in dados.get("tatuagens", [])],
        "passos": [dict(linha) for linha in dados.get("passos", [])],
    }, avisos


def exigir_campos(tabela: str, linhas: list[dict], campos: tuple[str, ...]) -> None:
    for linha in linhas:
        faltando = [
            campo
            for campo in campos
            if linha.get(campo) is None
            or (isinstance(linha.get(campo), str) and not linha[campo].strip())
        ]
        if faltando:
            raise SystemExit(
                f"{tabela}: linha {linha.get('id')} sem os campos "
                + ", ".join(faltando)
                + "."
            )


def filtrar_orfaos(
    linhas: list[dict],
    campo: str,
    permitidos: set,
    ignorar: bool,
    rotulo: str,
) -> tuple[list[dict], int]:
    orfaos = [linha for linha in linhas if linha.get(campo) not in permitidos]
    if orfaos and not ignorar:
        ids = ", ".join(str(linha.get("id")) for linha in orfaos[:15])
        raise SystemExit(
            f"{rotulo}: {len(orfaos)} linha(s) apontam para {campo} inexistente "
            f"(ids {ids}). Use --ignorar-orfaos para descartar essas linhas."
        )
    validas = [linha for linha in linhas if linha.get(campo) in permitidos]
    return validas, len(orfaos)


def converter(valor, tipo_postgres: str):
    if valor is None:
        return None
    if tipo_postgres == "date":
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        return valor
    if tipo_postgres in ("numeric", "decimal", "real", "double precision"):
        if not isinstance(valor, Decimal):
            return Decimal(str(valor))
        return valor
    if tipo_postgres in ("integer", "bigint", "smallint"):
        return int(valor)
    if tipo_postgres in ("character varying", "character", "text", "uuid"):
        if isinstance(valor, bytes):
            return valor.decode("utf-8")
        return str(valor)
    if tipo_postgres == "boolean":
        return bool(valor)
    return valor


def preparar_linhas(
    tabela: str,
    linhas: list[dict],
    colunas_destino: list[dict],
) -> tuple[list[str], list[tuple]]:
    nomes = [coluna["nome"] for coluna in colunas_destino]
    tipos = {coluna["nome"]: coluna["tipo"] for coluna in colunas_destino}
    valores = []
    for linha in linhas:
        if linha.get("id") is None:
            raise SystemExit(f"{tabela}: há linha sem id.")
        valores.append(
            tuple(converter(linha.get(nome), tipos[nome]) for nome in nomes)
        )
    return nomes, valores


def inserir(cursor, tabela: str, colunas: list[str], linhas: list[tuple]) -> None:
    if not linhas:
        return
    nomes = sql.SQL(", ").join(sql.Identifier(coluna) for coluna in colunas)
    atualizacoes = sql.SQL(", ").join(
        sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(coluna), sql.Identifier(coluna))
        for coluna in colunas
        if coluna != "id"
    )
    if not atualizacoes:
        conflito = sql.SQL("DO NOTHING")
    else:
        conflito = sql.SQL("DO UPDATE SET {}").format(atualizacoes)
    consulta = sql.SQL(
        "INSERT INTO {} ({}) VALUES %s ON CONFLICT (id) {}"
    ).format(sql.Identifier(tabela), nomes, conflito)
    execute_values(cursor, consulta.as_string(cursor), linhas, page_size=500)


def limpar_destino(cursor) -> None:
    cursor.execute(
        "TRUNCATE TABLE passos, tatuagens, usuarios, clientes "
        "RESTART IDENTITY CASCADE"
    )


def ajustar_sequencias(cursor) -> None:
    for tabela in ORDEM_DE_INSERCAO:
        cursor.execute(
            sql.SQL(
                "SELECT setval("
                "pg_get_serial_sequence({tabela_literal}, 'id'), "
                "COALESCE((SELECT MAX(id) FROM {tabela}), 1), "
                "(SELECT COUNT(*) > 0 FROM {tabela})"
                ")"
            ).format(
                tabela_literal=sql.Literal(tabela),
                tabela=sql.Identifier(tabela),
            )
        )


def imprimir_listagem(mysql_cursor, pg_cursor) -> None:
    mysql_cursor.execute("SELECT DATABASE() AS banco")
    banco = mysql_cursor.fetchone()["banco"]
    tabelas = listar_tabelas_mysql(mysql_cursor)
    print(f"MySQL: {banco or '(nenhum banco selecionado)'}")
    for nome in TABELAS_DADOS:
        tabela_real = tabelas.get(nome)
        if tabela_real is None:
            print(f"- {nome}: ausente")
            continue
        total = contar_mysql(mysql_cursor, tabela_real)
        print(f"- {nome}: {total} linha(s)")
        for coluna in colunas_mysql(mysql_cursor, tabela_real):
            nulo = "null" if coluna["permite_nulo"] == "YES" else "not null"
            chave = f" key={coluna['chave']}" if coluna["chave"] else ""
            print(
                f"    {coluna['nome']}: {coluna['tipo']} {nulo}{chave}"
            )

    print("Supabase:")
    for tabela in ORDEM_DE_INSERCAO:
        try:
            pg_cursor.execute(
                sql.SQL("SELECT COUNT(*) AS total FROM {}").format(
                    sql.Identifier(tabela)
                )
            )
            print(f"- {tabela}: {pg_cursor.fetchone()['total']} linha(s)")
        except psycopg2.errors.UndefinedTable:
            pg_cursor.connection.rollback()
            print(f"- {tabela}: tabela ausente")


def imprimir_resumo(dados: dict[str, list[dict]], avisos: list[str]) -> None:
    print("Origem MySQL:")
    for tabela in TABELAS_DADOS:
        print(f"- {tabela}: {len(dados.get(tabela, []))} linha(s)")
    if avisos:
        print("Avisos:")
        for aviso in avisos[:20]:
            print(f"- {aviso}")
        if len(avisos) > 20:
            print(f"- ... e mais {len(avisos) - 20} aviso(s).")


def main() -> int:
    args = argumentos()

    try:
        mysql = conectar_mysql(args)
    except pymysql.err.OperationalError as erro:
        codigo = erro.args[0] if erro.args else None
        if codigo == 1045:
            print("MySQL recusou o usuário ou a senha.")
        elif codigo == 1049:
            print(f"O banco MySQL '{args.banco}' não existe.")
        elif codigo == 2003:
            print(f"Não foi possível conectar ao MySQL em {args.host}:{args.porta}.")
        else:
            print(f"Erro ao conectar ao MySQL: {erro}")
        return 1

    try:
        if args.listar:
            try:
                pg = conectar_postgres()
            except psycopg2.OperationalError as erro:
                print("Não foi possível conectar ao PostgreSQL configurado em backend/.env.")
                print(erro)
                return 1
            try:
                with mysql.cursor() as mysql_cursor, pg.cursor(
                    cursor_factory=RealDictCursor
                ) as pg_cursor:
                    imprimir_listagem(mysql_cursor, pg_cursor)
            finally:
                pg.close()
            return 0

        with mysql.cursor() as mysql_cursor:
            tabelas = listar_tabelas_mysql(mysql_cursor)
            dados = carregar_dados(mysql_cursor, tabelas)

        try:
            pg = conectar_postgres()
        except psycopg2.OperationalError as erro:
            print("Não foi possível conectar ao PostgreSQL configurado em backend/.env.")
            print(erro)
            return 1

        try:
            with pg.cursor(cursor_factory=RealDictCursor) as pg_cursor:
                grupos = carregar_grupos(pg_cursor)
                proximo_id = proximo_id_usuarios(pg_cursor, dados)
                preparados, avisos = montar_dados(dados, grupos, args, proximo_id)

                exigir_campos("clientes", preparados["clientes"], ("id", "nome"))
                exigir_campos(
                    "usuarios",
                    preparados["usuarios"],
                    ("id", "nome", "email", "senha_hash", "papel", "grupo_id"),
                )
                exigir_campos(
                    "tatuagens",
                    preparados["tatuagens"],
                    ("id", "cliente_id", "ideia", "local_do_corpo", "tamanho", "etapa"),
                )
                exigir_campos(
                    "passos",
                    preparados["passos"],
                    ("id", "tatuagem_id", "tipo", "data"),
                )

                ids_clientes = {linha["id"] for linha in preparados["clientes"]}
                for usuario in preparados["usuarios"]:
                    cliente_id = usuario.get("cliente_id")
                    if cliente_id is not None and cliente_id not in ids_clientes:
                        avisos.append(
                            f"Usuário {usuario['id']} apontava para cliente "
                            f"{cliente_id} inexistente; cliente_id ficará nulo."
                        )
                        usuario["cliente_id"] = None

                preparados["tatuagens"], orfaos_tatuagens = filtrar_orfaos(
                    preparados["tatuagens"],
                    "cliente_id",
                    ids_clientes,
                    args.ignorar_orfaos,
                    "Tatuagens",
                )
                if orfaos_tatuagens:
                    avisos.append(
                        f"{orfaos_tatuagens} tatuagem(ns) órfã(s) foram ignoradas."
                    )

                ids_tatuagens = {linha["id"] for linha in preparados["tatuagens"]}
                preparados["passos"], orfaos_passos = filtrar_orfaos(
                    preparados["passos"],
                    "tatuagem_id",
                    ids_tatuagens,
                    args.ignorar_orfaos,
                    "Passos",
                )
                if orfaos_passos:
                    avisos.append(f"{orfaos_passos} passo(s) órfão(s) foram ignorados.")

                imprimir_resumo(dados, avisos)
                print("Preparado para gravar:")
                for tabela in ORDEM_DE_INSERCAO:
                    print(f"- {tabela}: {len(preparados[tabela])} linha(s)")

                if not args.executar:
                    pg.rollback()
                    print(
                        "Simulação concluída; nada foi gravado. "
                        "Use --executar para gravar."
                    )
                    return 0

                if args.limpar:
                    limpar_destino(pg_cursor)

                for tabela in ORDEM_DE_INSERCAO:
                    colunas_destino = colunas_postgres(pg_cursor, tabela)
                    colunas, valores = preparar_linhas(
                        tabela, preparados[tabela], colunas_destino
                    )
                    inserir(pg_cursor, tabela, colunas, valores)

                ajustar_sequencias(pg_cursor)
                pg.commit()
                print("Importação concluída e gravada no Supabase.")
                return 0
        except Exception:
            pg.rollback()
            raise
        finally:
            pg.close()
    finally:
        mysql.close()


if __name__ == "__main__":
    raise SystemExit(main())
