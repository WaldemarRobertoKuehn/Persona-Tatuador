# Traço Fino · estúdio de tatuagem

Sistema da **cartilha 4** da UC4: um estúdio de tatuagem pequeno, com dois tatuadores, em que as
etapas de cada tatuagem (pedido, desenho aprovado, sessões e retoque) ficam registradas em vez de
se perderem em conversa de mensagem.

A fonte do que o sistema precisa fazer é `docs/CARTILHA.md`, sem alteração. As decisões do projeto,
o que pode e o que não pode aparecer no código, estão em `REGRAS.md`.

## Estado atual

**O back está pronto e testado, e o front está pronto e testado.** Marca e styleguide estão
escritos, em `docs/marca.md` e `docs/styleguide/`. O front é servido e testado em
`http://localhost:5173`.

O back entrega as cinco coisas que a cartilha pede:

| capacidade da cartilha | rota |
| --- | --- |
| Listar as tatuagens, com filtro por etapa e por cliente | `GET /tatuagens?etapa=&cliente_id=` |
| Mostrar uma tatuagem | `GET /tatuagens/{tatuagem_id}` |
| Pedir uma tatuagem nova | `POST /tatuagens` |
| Listar os passos de uma tatuagem | `GET /tatuagens/{tatuagem_id}/passos` |
| Registrar um passo numa tatuagem | `POST /tatuagens/{tatuagem_id}/passos` |

A agenda abre com **oito tatuagens de demonstração** — cinco da Bruna e três da Camila — e os
históricos delas estão coerentes com a regra. Esses dados estão no MySQL, e foram criados pelo
`backend/esquema.sql`, no bloco `DADOS DE DEMONSTRAÇÃO` do fim do arquivo. Para a API nascer vazia,
rode o `esquema.sql` sem aquele bloco.

A agenda também mostra o nome da cliente, e não o `cliente_id`. O nome mora no back, em
`repositorios/cliente.py`, e entra na resposta como `nome_da_cliente`. A cartilha lista o usuário
como uma das três entidades, e nome é dado do negócio, não dado de tela: guardar no front
significaria o mesmo nome escrito em dois lugares, divergindo na primeira correção. Esse depósito
não tem rota, porque a cartilha não pede rota de cliente.

O logo também não é duplicado. Os arquivos da marca ficam em `docs/marca/`, que é onde a REGRAS pede
que fiquem, e o Vite serve aquela pasta como arquivo estático, com `publicDir` em
`frontend/vite.config.js`. A tela pede `/logo.svg` e recebe o arquivo que está versionado, sem
cópia nenhuma dentro do front.

```
.
├── docs/            o que não é código
│   ├── CARTILHA.md  a cartilha sorteada, sem alteração
│   ├── BRIEFING.md  o briefing, escrito por mim
│   ├── COMO_RODAR.md o passo a passo de abrir e de fechar os dois servidores
│   ├── marca.md     o que a marca é e as regras de uso
│   ├── marca/       os arquivos da marca, que o front serve de lá
│   └── styleguide/  o styleguide, ou o link do Figma
├── frontend/        o React, com as quatro telas
│   ├── src/
│   │   ├── componentes/  o logo, o botão de tema e as peças repetidas
│   │   ├── estilos/      os tokens do styleguide e o CSS das telas
│   │   ├── fontes/       a Playfair Display, com a licença e a procedência
│   │   ├── imagens/      as fotos do ateliê, da vitrine e dos dois perfis
│   │   ├── telas/        as quatro telas da cartilha e a escolha de perfil
│   │   ├── api.js        o único lugar do front que fala com o back
│   │   ├── datas.js      ISO do back virando dd/mm/aaaa na tela
│   │   ├── perfis.js     os perfis fixos e a ordem das telas de cada um
│   │   └── tema.js       o tema da tela e o botão que o troca
│   ├── index.html    a página, e o script que aplica o tema antes de pintar
│   └── vite.config.js onde o Vite serve a marca, sem copiar
├── backend/         a API, com FastAPI
│   ├── .env         o que muda de máquina para máquina, fora do Git
│   ├── .env.exemplo as mesmas chaves, sem os valores, dentro do Git
│   ├── configuracao.py  o único arquivo que lê o .env
│   ├── banco.py          o engine, a fábrica Sessao, a Base e o obter_sessao
│   ├── esquema.sql       o desenho do banco, que o MySQL roda de uma vez
│   ├── alembic.ini       a configuração do Alembic, sem a senha
│   ├── migracoes/        o env.py, onde o Alembic acha os modelos e o banco
│   │   └── versions/     uma migration por arquivo, e elas vão para o Git
│   ├── modelos/          o desenho das tabelas, uma classe por entidade
│   ├── main.py          cria o app, registra o CORS e liga os routers
│   ├── rotas/           o que conhece HTTP
│   ├── servicos/        as decisões e a regra da cartilha
│   ├── repositorios/    as funções que leem e gravam no banco
│   │   └── cliente.py       o nome de quem é dona da tatuagem
│   └── esquemas/        o formato de entrada e de saída
├── REGRAS.md        as regras do projeto para a IA
└── README.md        este arquivo
```

## Como rodar o back

> O passo a passo completo de abrir e de fechar os dois está em
> [`docs/COMO_RODAR.md`](docs/COMO_RODAR.md).

O back é o FastAPI, na pasta `backend/`. A documentação automática fica em `/docs`.

O banco é o **MySQL**, e ele precisa existir antes do back subir. O desenho dele está em
`backend/esquema.sql`, que cria as três tabelas e já entra com os dados de demonstração:

```bash
mysql -u root -p < esquema.sql
```

A senha é pedida pelo próprio `mysql`, não vai no comando.

Depois, o ambiente do Python. São sete pacotes, e cada um tem um porquê:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi fastapi-cli "uvicorn[standard]" sqlalchemy mysql-connector-python python-dotenv alembic
```

| pacote | por que |
| --- | --- |
| `fastapi` | `FastAPI`, `APIRouter`, `HTTPException`, `Query` e `Depends`, em `main.py` e `rotas/` |
| `fastapi-cli` | o comando `fastapi dev`. Sem ele o `fastapi.exe` avisa que falta o `fastapi[standard]` |
| `uvicorn[standard]` | o servidor que o `fastapi dev` sobe, e o `watchfiles`, que é o auto-reload |
| `sqlalchemy` | `create_engine`, `sessionmaker`, `DeclarativeBase`, `Column`, `ForeignKey` e `relationship`, em `banco.py` e `modelos/` |
| `mysql-connector-python` | o driver `mysql+mysqlconnector`, que é o que o `configuracao.py` monta |
| `python-dotenv` | o `load_dotenv()` do `configuracao.py` |
| `alembic` | o comando `alembic` e o `migracoes/env.py`, para as migrations |

O `pydantic` não está na lista porque vem junto com o `fastapi`, e o `starlette` também.

E aí o back sobe:

```bash
fastapi dev main.py
```

Com o back no ar, o esperado é:

- o terminal mostrar `http://localhost:8000`;
- abrir `http://localhost:8000/docs` e ver as cinco rotas da tabela acima;
- `GET http://localhost:8000/tatuagens` responder com as **oito tatuagens de demonstração**, e
  `?etapa=em sessões` devolver só três.

A raiz `http://localhost:8000` responde **404**, e isso é de propósito: as REGRAS proíbem rota no
`main.py`.

O `.env` precisa ter `ORIGEM_FRONTEND` com o endereço exato do front, porque é dele que sai o CORS.
Se o endereço mudar, mude no `.env` e reinicie o back.

## Mudança no banco: migrations

O banco é o MySQL, e o desenho dele mora nos modelos, em `backend/modelos/`. O problema do
`Base.metadata.create_all` é que ele **só cria a tabela que ainda não existe**: tabela que já
existe, ele não toca. Mudar uma coluna ou acrescentar uma chave estrangeira numa tabela que já tem
dado de alguém não pode ser `DROP TABLE` nem `ALTER TABLE` escrito à mão, porque um funciona só na
máquina de quem escreveu e o outro ninguém lembra.

É para isso que o projeto usa o **Alembic**, que é o commit do banco: um arquivo `.py` por mudança,
em `backend/migracoes/versions/`, que vai para o Git. O endereço do banco **não** fica no
`alembic.ini`: ele vem do `.env`, pelo `configuracao.py`, e o `migracoes/env.py` entrega ao Alembic o
mesmo `engine` que a API usa.

Os quatro comandos, rodados no terminal de `backend/`, com o venv ativo:

| comando | quando usar |
| --- | --- |
| `alembic revision --autogenerate -m "o que mudou"` | mudou um modelo: o Alembic compara os modelos com o banco e escreve a migration com a diferença |
| `alembic upgrade head` | aplica no banco o que ainda falta |
| `alembic current` | diz em que migration o banco está |
| `alembic history` | lista as migrations, da mais nova para a mais velha |

O passo é sempre o mesmo, e a ordem importa: mudo o modelo, gero a migration, **leio o arquivo
gerado** e só então aplico com `alembic upgrade head`. O `--autogenerate` acerta tabela, coluna e
chave; em troca de nome de coluna ele não é confiável, porque lê como apagar uma e criar outra.

**O banco atual ainda não tem migration.** As duas chaves estrangeiras (`fk_tatuagens_cliente` e
`fk_passos_tatuagem`) já estão no MySQL, e `backend/esquema.sql` é o desenho que as criou. A pasta
`migracoes/versions/` começa vazia de propósito: o banco foi montado direto do desenho, sem passar
por migration, e a primeira migration vai nascer da **primeira mudança de verdade** que vier. Como o
Alembic compara os modelos com o banco que está rodando, e não com a pasta de migrations, essa
primeira migration sai com só a diferença do dia, sem nada do que já estava lá.

Conferindo o estado sem escrever nada: `alembic check` responde `No new upgrade operations detected`
quando o banco bate com os modelos.

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

As quatro telas da cartilha estão escritas. Escolhendo Bruna, "Minhas tatuagens" mostra as cinco
tatuagens dela, com a etapa de cada uma e o histórico ao clicar em "Ver histórico", e "Pedir
tatuagem" grava no back e volta com a etapa `pedida`. Escolhendo Vitor, "A agenda" lista as oito
tatuagens do estúdio com filtro por etapa, e "Abrir ficha" abre a ficha de uma delas, onde o passo
é registrado. A ficha mostra os dois resultados do back: quando a regra aceita, a etapa nova
aparece; quando a regra recusa, o motivo aparece embaixo do campo, e a etapa não muda.

### A cara da tela

A entrada tem a foto do ateliê e uma vitrine, e os dois perfis são cartões com retrato. A barra
fixa do alto é a mesma nas quatro telas: logo, plaquinha do estúdio, quem está usando e o botão de
tema. Cada tatuagem ganha a linha do tempo das quatro etapas em cima do botão do histórico, e o
histórico é desenhado como uma linha do tempo com um ponto por passo.

Tudo isso é CSS em `estilos/base.css`, e nada disso é uma cor nova: as cores continuam sendo só as
do styleguide, seção 1. As fotos são importadas como arquivo (`import`), e não com caminho escrito
à mão, que é o que faz o `npm run build` copiá-las para dentro do `dist`.

### O que a tela não pode fazer

O visual do AI Studio foi copiado para dentro do styleguide, e não por cima dele. Três coisas dele
ficaram de fora, e vale saber por quê:

- **O texto da regra da cartilha não foi para a ficha.** A versão do AI Studio escrevia embaixo do
  campo de qual etapa aceita qual passo. A regra é do serviço, no back: copiar para a tela criaria
  duas regras que divergem na primeira correção. A ficha mostra os três passos sempre, e o motivo
  da recusa vem do back.
- **Sem gradiente no hero.** O styleguide seção 6 proíbe, e texto por cima de foto não tem contraste
  garantido — o que garante contraste é a tabela da seção 1.
- **Sem emoji no botão de tema.** O botão continua sendo "Tema escuro" em texto, pela mesma regra
  que proíbe ícone no lugar de palavra.

### A marca e a fonte não pedem internet

Duas coisas da tela vêm de arquivos do próprio repositório, e isso é escolha, não sorte:

- **O logo.** Os SVG estão em `docs/marca/` e o `vite.config.js` serve aquela pasta com
  `publicDir`, então a tela pede `/logo.svg` e recebe o arquivo versionado. Não existe cópia do
  logo dentro do `frontend/`. No tema escuro ela pede o `/logo-escuro.svg`, que já foi desenhado
  com a palavra em branco: trocar de arquivo, e não repintar por CSS, porque um logo que mudasse
  de cor conforme o fundo seria uma versão da marca que ninguém desenhou.
- **A fonte.** A Playfair Display está em `src/fontes/playfair-display.woff2`, com a `@font-face`
  em `estilos/tokens.css`. É um link a menos para fora, e a apresentação funciona sem internet. A
  pasta tem um `LEIA-ME.md` com a origem e a licença, que é a SIL Open Font License 1.1.

A letra do logo está desenhada em curva (`<path>`), e não como texto. Um SVG aberto com `<img>` é
um documento separado que não enxerga a fonte da página, então a letra escrita como texto
apareceria na Georgia em toda máquina sem a Playfair Display instalada — e o favicon, que é o
símbolo, ficaria diferente em cada computador.

### O tema

O botão "Tema escuro", no canto do cabeçalho, alterna a tela inteira. A escolha fica guardada no
navegador e vale para as visitas seguintes. Quem nunca escolheu vê o tema do sistema operacional, e
a tela já abre na cor certa, porque o `index.html` tem um script no `<head>` que aplica o tema
antes de a página pintar — sem ele, a tela apareceria branca e viraria escura um instante depois.

As duas paletas e os contrastes de cada uma estão no `docs/styleguide/styleguide.md`. O escuro não
é o claro invertido: ele repete preto, branco e o mesmo laranja de acento, com valores próprios.

## Regras de ouro deste repositório

- Rota chama serviço, serviço chama repositório. Nunca o contrário.
- Os dados ficam no MySQL, e o desenho do banco mora nos modelos, em `modelos/`. A sessão nasce na
  rota, pelo `Depends(obter_sessao)`, e passa de mão em mão.
- Mudança numa tabela que já existe é migration, em `migracoes/versions/`, versionada no Git. Nunca
  `DROP TABLE` e nunca `ALTER TABLE` escrito à mão.
- A regra da cartilha mora no serviço. Quando ela recusa, o serviço devolve `None` ou o motivo, e
  é a rota que escolhe o status.
- `async def` não entra. Rota é `def` normal.
- CORS liberado só para o endereço do front, lido do `.env`. Nunca `["*"]`.
- Perfil é escolhido numa lista, sem senha. A tela da pessoa diz quem ela é na requisição.
- Cor mora em token, em `estilos/tokens.css`. Nenhuma tela escreve um código de cor, e nenhum
  hexadecimal sobrou no CSS: até o branco do botão principal é `--cor-sobre-acento`.
- A marca não é duplicada no front, e a fonte não vem de link. As duas coisas vêm do repositório.
