# Traço Fino · estúdio de tatuagem

Sistema da **cartilha 4** da UC4: um estúdio de tatuagem pequeno, com dois tatuadores, em que as
etapas de cada tatuagem (pedido, desenho aprovado, sessões e retoque) ficam registradas em vez de
se perderem em conversa de mensagem.

A fonte do que o sistema precisa fazer é `docs/CARTILHA.md`, sem alteração. As decisões do projeto,
o que pode e o que não pode aparecer no código, estão em `REGRAS.md`.

## Estado atual

**O back está pronto e testado, e o front está começado.** Marca e styleguide estão escritos, em
`docs/marca/` e `docs/styleguide/`. O único commit do Git é o do briefing: o resto do trabalho está
na árvore, sem commit.

O back entrega as cinco coisas que a cartilha pede:

| capacidade da cartilha | rota |
| --- | --- |
| Listar as tatuagens, com filtro por etapa e por cliente | `GET /tatuagens?etapa=&cliente_id=` |
| Mostrar uma tatuagem | `GET /tatuagens/{tatuagem_id}` |
| Pedir uma tatuagem nova | `POST /tatuagens` |
| Listar os passos de uma tatuagem | `GET /tatuagens/{tatuagem_id}/passos` |
| Registrar um passo numa tatuagem | `POST /tatuagens/{tatuagem_id}/passos` |

A agenda abre com **cinco tatuagens de demonstração**, uma em cada etapa, e os históricos delas
estão coerentes com a regra. Esses dados ficam no fim de cada arquivo de `repositorios/`, e é só
apagar o bloco `..._de_exemplo` se você quiser a API vazia.

A agenda também mostra o nome da cliente, e não o `cliente_id`. O nome mora no back, em
`repositorios/cliente.py`, e entra na resposta como `nome_da_cliente`. A cartilha lista o usuário
como uma das três entidades, e nome é dado do negócio, não dado de tela: guardar no front
significaria o mesmo nome escrito em dois lugares, divergindo na primeira correção. Esse depósito
não tem rota, porque a cartilha não pede rota de cliente.

```
.
├── docs/            o que não é código
│   ├── CARTILHA.md  a cartilha sorteada, sem alteração
│   ├── BRIEFING.md  o briefing, escrito por mim
│   ├── marca/       o logo e as versões dele
│   └── styleguide/  o styleguide, ou o link do Figma
├── frontend/        o React, com as quatro telas
├── backend/         a API, com FastAPI
│   ├── .env         o que muda de máquina para máquina, fora do Git
│   ├── .env.exemplo as mesmas chaves, sem os valores, dentro do Git
│   ├── configuracao.py  o único arquivo que lê o .env
│   ├── main.py          cria o app, registra o CORS e liga os routers
│   ├── rotas/           o que conhece HTTP
│   ├── servicos/        as decisões e a regra da cartilha
│   ├── repositorios/    a lista em memória
│   │   └── cliente.py       o nome de quem é dona da tatuagem
│   └── esquemas/        o formato de entrada e de saída
├── REGRAS.md        as regras do projeto para a IA
└── README.md        este arquivo
```

## Como rodar o back

O back é o FastAPI, na pasta `backend/`. A documentação automática fica em `/docs`.

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi "uvicorn[standard]" python-dotenv
fastapi dev main.py
```

Com o back no ar, o esperado é:

- o terminal mostrar `http://localhost:8000`;
- abrir `http://localhost:8000/docs` e ver as cinco rotas da tabela acima;
- `GET http://localhost:8000/tatuagens` responder com as **cinco tatuagens de demonstração**, e
  `?etapa=em sessões` devolver só duas. A lista em memória morre quando o processo reinicia.

A raiz `http://localhost:8000` responde **404**, e isso é de propósito: as REGRAS proíbem rota no
`main.py`.

O `.env` precisa ter `ORIGEM_FRONTEND` com o endereço exato do front, porque é dele que sai o CORS.
Se o endereço mudar, mude no `.env` e reinicie o back.

## Como rodar o front

O front é o React, na pasta `frontend/`. Ele precisa do back no ar, porque todas as telas chamam a
API. Só React e React DOM são dependência de execução: não há biblioteca de rotas, nem de requisição,
porque a cartilha tem quatro telas e não precisa de mais que isso.

```bash
cd frontend
npm install
npm run dev
```

O esperado é o Vite abrir `http://localhost:5173` e a tela de escolha de perfil aparecer, com a
Bruna e o Vitor. Esse endereço tem que ser igual ao `ORIGEM_FRONTEND` do `.env` do back, senão o
navegador bloqueia a chamada por CORS.

As quatro telas da cartilha estão escritas. Escolhendo Bruna, "Minhas tatuagens" mostra as três
tatuagens dela, com a etapa de cada uma e o histórico ao clicar em "Ver histórico", e "Pedir
tatuagem" grava no back e volta com a etapa `pedida`. Escolhendo Vitor, "A agenda" lista as cinco
tatuagens do estúdio com filtro por etapa, e "Abrir ficha" abre a ficha de uma delas, onde o passo
é registrado. A ficha mostra os dois resultados do back: quando a regra aceita, a etapa nova
aparece; quando a regra recusa, o motivo aparece embaixo do campo, e a etapa não muda.

## Regras de ouro deste repositório

- Rota chama serviço, serviço chama repositório. Nunca o contrário.
- Os dados ficam em lista na memória, dentro do repositório. Sem banco, sem ORM.
- A regra da cartilha mora no serviço. Quando ela recusa, o serviço devolve `None` ou o motivo, e
  é a rota que escolhe o status.
- `async def` não entra. Rota é `def` normal.
- CORS liberado só para o endereço do front, lido do `.env`. Nunca `["*"]`.
- Perfil é escolhido numa lista, sem senha. A tela da pessoa diz quem ela é na requisição.
