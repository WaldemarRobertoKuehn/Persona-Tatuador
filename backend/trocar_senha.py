"""Troca a senha de uma conta, no terminal.

Roda com `python trocar_senha.py email novassenha`, de dentro de backend/. É a
manutenção de conta do banco de estudo: o caminho normal para trocar a senha de
uma pessoa é a tela, e esta tela não existe no sistema ainda.

Por que a senha pode precisar ser trocada

    O hash da senha não tem volta: é uma via de mão só. Se a senha se perde, o
    jeito de recuperar a conta é gerar um hash novo para ela, e é o que este
    arquivo faz. O mesmo vale para quem nunca soube a senha: a conta existe, o
    hash existe, mas não há senha que abra a porta.

O que este arquivo não faz

    Ele não escreve a senha em texto no banco, e não imprime o hash. Quem
    calcula o hash é o serviço, que é o mesmo do cadastro, e o que sai daqui é
    só a confirmação de que a senha foi trocada.
"""

# sys.argv são os argumentos que o terminal passou, depois do nome do arquivo.
import sys

# O serviço, que é a camada que calcula o hash: este arquivo não sabe como
# senha é guardada, e é por isso que ele não importa o seguranca.
import servicos.usuario as servico_usuarios


# Sem email e sem senha nova o arquivo não sabe o que fazer, e sair com uma
# mensagem é melhor do que quebrar com um traceback.
if len(sys.argv) != 3:
    print("Uso: python trocar_senha.py email novassenha")
    sys.exit(1)

email = sys.argv[1]
senha_nova = sys.argv[2]

# A senha mínima é a mesma do esquema de cadastro: oito caracteres.
if len(senha_nova) < 8:
    print("A senha nova precisa de pelo menos 8 caracteres.")
    sys.exit(1)

if servico_usuarios.trocar_senha(email, senha_nova):
    print(f"Senha trocada para a conta {email}.")
else:
    print(f"Nao existe conta com o email {email}.")
    sys.exit(1)
