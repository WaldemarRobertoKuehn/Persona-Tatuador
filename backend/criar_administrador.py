"""NOVO: cria a primeira conta Administrador por comando local interativo."""

from getpass import getpass

import repositorios.grupo as repositorio_grupos
import repositorios.usuario as repositorio_usuarios
import servicos.usuario as servico_usuarios
from esquemas.usuario import UsuarioCadastro


def main() -> None:
    """NOVO: solicita credenciais sem expor senha em argumentos ou no código."""
    if repositorio_grupos.contar_administradores() > 0:
        print("Já existe uma conta Administrador.")
        return

    nome = input("Nome do Administrador: ").strip()
    email = input("E-mail do Administrador: ").strip().lower()
    senha = getpass("Senha (mínimo de 8 caracteres): ")
    confirmacao = getpass("Confirme a senha: ")

    if senha != confirmacao:
        raise ValueError("As senhas não coincidem.")
    # NOVO: reutiliza as validações de nome, e-mail e senha do cadastro da API.
    credenciais = UsuarioCadastro(nome=nome, email=email, senha=senha)
    nome = credenciais.nome
    email = credenciais.email
    senha = credenciais.senha
    if repositorio_usuarios.buscar_por_email(email) is not None:
        raise ValueError("Já existe uma conta com este e-mail.")

    # NOVO: grupo Administrador e permissões são provisionados pela migration.
    administrador = servico_usuarios.cadastrar(
        {
            "nome": nome,
            "email": email,
            "senha": senha,
            "papel": "administrador",
        }
    )
    if administrador is None:
        raise RuntimeError("Não foi possível criar a conta Administrador.")
    print(f"Conta Administrador criada para {administrador['email']}.")


if __name__ == "__main__":
    main()
