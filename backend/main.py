"""Monta a aplicação e liga as partes.

Este arquivo cria o app, registra o CORS e, mais para frente, liga os routers das
rotas. Nenhuma rota mora aqui: rota pertence a backend/rotas/, e a regra do projeto
é que este arquivo só amarra as peças.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import de módulo com `import configuracao`: o main chama a configuração pelo nome
# do arquivo, sem puxar para dentro dela nenhuma função solta.
import configuracao

# NOVO: os routers são importados sem trazer as funções de rota para este módulo;
# o main continua apenas conectando cada recurso à aplicação.
from rotas import passos as rotas_passos
from rotas import autenticacao as rotas_autenticacao
# NOVO: o router de grupos oferece gestão administrativa de permissões.
from rotas import grupos as rotas_grupos
from rotas import health as rotas_health
from rotas import tatuagens as rotas_tatuagens
from rotas import usuarios as rotas_usuarios

# O FastAPI é o objeto que carrega a aplicação e onde as rotas vão ser registradas.
# Ele nasce vazio, e o include_router é quem vai preencher.
app = FastAPI(title="Traço Fino", version="0.1.0")

# CORSMiddleware é o que autoriza o front, que roda em um endereço, a chamar a API,
# que roda em outro. Sem ele, o navegador bloqueia a chamada.
# allow_origins recebe uma lista, e não a string "*": a regra do projeto exige o
# endereço exato do meu front, e esse endereço vem da configuração, nunca do código.
# NOVO: PUT é necessário para atribuir usuários a grupos e alterar permissões.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracao.endereco_do_front()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"],
)

# include_router é quem pendura as rotas do projeto dentro do app. Um include por
# arquivo de backend/rotas/, e o prefixo de cada uma já está no próprio router.
# Cada include registra um recurso; as rotas administrativas continuam nos
# próprios módulos e o main não declara nenhuma rota.
app.include_router(rotas_tatuagens.roteador_tatuagens)
app.include_router(rotas_passos.roteador_passos)
app.include_router(rotas_usuarios.roteador_usuarios)
app.include_router(rotas_autenticacao.roteador_autenticacao)
# NOVO: endpoint administrativo de grupos e permissões.
app.include_router(rotas_grupos.roteador_grupos)
app.include_router(rotas_health.roteador_health)
