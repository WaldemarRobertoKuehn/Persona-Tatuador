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

# Os dois routers são importados pelo módulo. O main não sabe o que tem dentro de
# nenhum dos dois: ele só os liga no app.
from rotas import passos as rotas_passos
from rotas import tatuagens as rotas_tatuagens

# O FastAPI é o objeto que carrega a aplicação e onde as rotas vão ser registradas.
# Ele nasce vazio, e o include_router é quem vai preencher.
app = FastAPI(title="Traço Fino", version="0.1.0")

# CORSMiddleware é o que autoriza o front, que roda em um endereço, a chamar a API,
# que roda em outro. Sem ele, o navegador bloqueia a chamada.
# allow_origins recebe uma lista, e não a string "*": a regra do projeto exige o
# endereço exato do meu front, e esse endereço vem da configuração, nunca do código.
# allow_methods fica só com GET e POST porque são os únicos verbos que a cartilha
# pede. Se entrar rota com outro verbo, é só acrescentar o nome nesta lista.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[configuracao.endereco_do_front()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# include_router é quem pendura as rotas do projeto dentro do app. Um include por
# arquivo de backend/rotas/, e o prefixo de cada uma já está no próprio router.
# Depois destas duas linhas, as cinco capacidades da cartilha estão no ar, e o
# main continua sem nenhuma rota em si: ele só amarra as peças.
app.include_router(rotas_tatuagens.roteador_tatuagens)
app.include_router(rotas_passos.roteador_passos)
