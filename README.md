# Traço Fino · estúdio de tatuagem

Sistema da **cartilha 4** da UC4: um estúdio de tatuagem pequeno, com dois tatuadores, em que as
etapas de cada tatuagem (pedido, desenho aprovado, sessões e retoque) ficam registradas em vez de
se perderem em conversa de mensagem.

A fonte do que o sistema precisa fazer é `docs/CARTILHA.md`, sem alteração. As decisões do projeto,
o que pode e o que não pode aparecer no código, estão em `REGRAS.md`. O desenho das camadas, dos
fluxos e do deploy está em `docs/ARQUITETURA.md`.

## Estado atual

**O back está pronto e testado, e o front está pronto e testado.** Marca e styleguide estão
escritos, em `docs/marca.md` e `docs/styleguide/`. O front é servido e testado em
`http://localhost:5173`.

O cadastro público cria somente contas Cliente e, ao terminar, volta para o login sem iniciar uma
sessão. A tela de entrada também permite pedir redefinição por email; quem já está conectado pode
alterar a própria senha confirmando a senha atual. O envio depende de SMTP configurado no backend.
Cliente, Tatuador e Administrador têm rótulos e áreas de acesso distintos. A barra usa iniciais do
nome da conta, não as fotos das personas de demonstração.

O back entrega as cinco capacidades que a cartilha pede:

| capacidade da cartilha | rota |
| --- | --- |
| Listar as tatuagens, com filtro por etapa e por cliente | `GET /tatuagens?etapa=&cliente_id=` |
| Mostrar uma tatuagem | `GET /tatuagens/{tatuagem_id}` |
| Pedir uma tatuagem nova | `POST /tatuagens` |
| Listar os passos de uma tatuagem | `GET /tatuagens/{tatuagem_id}/passos` |
| Registrar um passo numa tatuagem | `POST /tatuagens/{tatuagem_id}/passos` |

Além delas, o sistema tem as capacidades que foram acrescentadas depois da cartilha:

| capacidade | rota |
| --- | --- |
| Entrar, cadastrar Cliente e trocar senha | `POST /autenticacao/login`, `POST /usuarios`, `POST /autenticacao/esqueci-senha`, `POST /autenticacao/redefinir-senha`, `POST /autenticacao/alterar-senha` |
| Consultar o próprio perfil | `GET /usuarios/eu` |
| Cadastrar e listar tatuadores | `POST /usuarios/tatuadores`, `GET /usuarios/tatuadores` |
| Atribuir o tatuador responsável pela tatuagem | `PUT /tatuagens/{tatuagem_id}/tatuador` |
| Enviar, listar, baixar e remover imagens | `POST/GET /tatuagens/{tatuagem_id}/imagens`, `GET/DELETE /tatuagens/{tatuagem_id}/imagens/{imagem_id}` |
| Aprovar ou recusar o desenho | `POST /tatuagens/{tatuagem_id}/imagens/{imagem_id}/aprovacao`, `.../recusa` |
| Consultar e marcar a agenda | `GET/POST /tatuagens/{tatuagem_id}/agendamentos`, `GET .../disponibilidade`, `DELETE .../{agendamento_id}` |
| Administrar grupos e permissões | `GET/POST /grupos`, `PUT /grupos/{grupo_id}/permissoes`, `GET /grupos/permissoes`, `PUT /usuarios/{usuario_id}/grupo` |

As imagens ficam no próprio PostgreSQL, na coluna `conteudo` de `tatuagem_imagens`, e o download é
autenticado. A agenda é do tatuador responsável: cada sessão ou retoque ocupa um bloco de uma hora,
e o índice único parcial impede dois agendamentos ativos no mesmo horário do mesmo profissional.

A agenda abre com **oito tatuagens de demonstração** — cinco da Bruna e três da Camila —, cada uma
com tatuador responsável e histórico coerente com a regra. Esses dados estão no PostgreSQL, e as
contas que entram nele estão na tabela `usuarios`: são criadas por
`backend/criar_contas_de_demonstracao.py`, que é o mesmo caminho do `criar_tabelas.py` e do
`alembic upgrade head`, ou seja, montagem de banco, e não rota da API.

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
├── .docs/           o diário de obra: IA, infraestrutura e próximos passos
├── docs/            o que não é código
│   ├── ARQUITETURA.md o desenho das camadas, dos fluxos e do deploy
│   ├── CARTILHA.md  a cartilha sorteada, sem alteração
│   ├── BRIEFING.md  o briefing, escrito por mim
│   ├── COMO_RODAR.md o passo a passo de abrir e de fechar os dois servidores
│   ├── DER.md       o desenho do banco, coluna por coluna
│   ├── marca.md     o que a marca é e as regras de uso
│   ├── marca/       os arquivos da marca, que o front serve de lá
│   └── styleguide/  o styleguide, ou o link do Figma
├── .env             o que muda de máquina para máquina, fora do Git
├── .env.exemplo     as mesmas chaves, sem os valores, dentro do Git
├── api/index.py     a entrada da API quando o deploy usa a raiz da Vercel
├── vercel.json      o deploy alternativo que serve o front e a API juntos
├── docker-compose.yml  caminho legado em contêiner, ainda com MySQL
├── Caddyfile        proxy HTTP local e arquivos do build do React
├── frontend/        o React, com as telas de cliente, tatuador, administrador e acesso
│   ├── .env.development / .env.production  o endereço da API em cada ambiente
│   ├── vercel.json  o proxy /api do projeto de front separado
│   ├── src/
│   │   ├── componentes/  logo, tema, senha, avisos, imagens, agenda e linha do tempo
│   │   ├── estilos/      os tokens do styleguide e o CSS das telas
│   │   ├── fontes/       a Playfair Display, com a licença e a procedência
│   │   ├── imagens/      as fotos do ateliê e da vitrine
│   │   ├── telas/        as telas da cartilha, login, administração e alteração de senha
│   │   ├── api.js        o único lugar do front que fala com o back
│   │   ├── App.jsx       a conta autenticada, a tela atual e a tatuagem aberta
│   │   ├── datas.js      ISO do back virando dd/mm/aaaa na tela
│   │   ├── perfis.js     os perfis e a ordem das telas de cada papel
│   │   └── tema.js       o tema da tela e o botão que o troca
│   ├── index.html    a página, e o script que aplica o tema antes de pintar
│   └── vite.config.js onde o Vite serve a marca, sem copiar
├── backend/         a API, com FastAPI
│   ├── .env.exemplo exemplo do formato do .env da raiz
│   ├── configuracao.py  o único arquivo que lê o .env
│   ├── banco.py          o engine, o cursor por requisição e a Base
│   ├── seguranca.py      o hash de senha e o JWT HS256
│   ├── criar_tabelas.py  aplica as migrations em um banco vazio
│   ├── criar_contas_de_demonstracao.py  as contas de demonstração
│   ├── criar_administrador.py / promover_administrador.py  o primeiro Administrador
│   ├── trocar_senha.py   troca local de senha, sem passar pela API
│   ├── importar_mysql_para_supabase.py  migração avulsa do banco antigo
│   ├── alembic.ini       a configuração do Alembic, sem a senha
│   ├── migracoes/        o env.py, onde o Alembic acha os modelos e o banco
│   │   └── versions/     uma migration por arquivo, e elas vão para o Git
│   ├── modelos/          o desenho das tabelas, uma classe por entidade
│   ├── main.py          cria o app, registra o CORS e liga os routers
│   ├── rotas/           o que conhece HTTP
│   ├── servicos/        as decisões e a regra da cartilha
│   ├── repositorios/    as funções que leem e gravam no banco
│   ├── esquemas/        o formato de entrada e de saída
│   └── tests/           os testes unitários dos serviços
├── REGRAS.md        as regras do projeto para a IA
└── README.md        este arquivo
```

## Como rodar o back

> O passo a passo completo de abrir e de fechar os dois está em
> [`docs/COMO_RODAR.md`](docs/COMO_RODAR.md).

O back é o FastAPI, na pasta `backend/`. A documentação automática fica em `/docs`.

## Publicar na Vercel

O frontend e o backend são dois projetos independentes da Vercel, conectados ao
mesmo repositório. Crie um projeto para cada pasta e configure o **Root Directory**
de acordo com a tabela:

| projeto | Root Directory | configuração de build |
| --- | --- | --- |
| Backend | `backend/` | Framework Preset `Other`; deixe os comandos de instalação e build padrão; a Vercel instala `requirements.txt` |
| Frontend | `frontend/` | Framework Preset `Vite`; Build Command `npm run build`; Output Directory `dist`; Install Command `npm install` |

No projeto do backend, `api/index.py` encaminha as requisições para o FastAPI.
O `requirements.txt` dessa pasta declara as dependências necessárias para uma
instalação limpa na Vercel.

Configure estas variáveis no projeto Vercel, em **Settings → Environment Variables**:

| variável | valor |
| --- | --- |
| `SUPABASE_DB_URL` | URL do PostgreSQL do Supabase (pooler), acessível pela Vercel |
| `SUPABASE_DB_PASSWORD` | senha do banco; fica separada da URL para não precisar de escape |
| `BANCO_SSLMODE` | `require` |
| `JWT_SEGREDO` | segredo aleatório com pelo menos 32 caracteres |
| `JWT_MINUTOS` | validade do token em minutos, por exemplo `60` |
| `ORIGEM_FRONTEND` | URL HTTPS exata do domínio onde o frontend está hospedado |
| `SMTP_HOST` | host do serviço de email com STARTTLS |
| `SMTP_PORT` | porta SMTP com STARTTLS, normalmente `587` |
| `SMTP_USER` | usuário SMTP |
| `SMTP_PASSWORD` | senha ou senha de aplicativo SMTP |
| `SMTP_FROM_EMAIL` | endereço remetente autorizado pelo provedor SMTP |

O `configuracao.py` também aceita um PostgreSQL local ou outro provedor pelas variáveis
`BANCO_HOST`, `BANCO_PORTA`, `BANCO_NOME`, `BANCO_USUARIO` e `BANCO_SENHA`, usadas quando
`SUPABASE_DB_URL` não está preenchida. O caminho usado hoje é o Supabase.

No projeto do frontend, para usar o proxy incluído em `frontend/vercel.json`,
mantenha `VITE_URL_DA_API=/api` (como em `frontend/.env.production`) e ajuste
nesse arquivo o domínio para o projeto Backend da Vercel. O proxy remove o
prefixo `/api` ao encaminhar a chamada: por exemplo, `/api/usuarios` chega ao
backend como `/usuarios`. Se preferir chamar o backend diretamente, configure
`VITE_URL_DA_API` somente com a URL base dele, sem acrescentar `/api`.

Na raiz deste repositório, `vercel.json` monta o front em `frontend/dist` e encaminha
`/api/*` para a função `api/index.py`, que importa o app de `backend/main.py`. Esse é
o desenho de projeto único. Para os dois projetos separados, selecione `frontend/` e
`backend/` como Root Directory de cada projeto.

Use um PostgreSQL hospedado externamente, pois um banco local da máquina não fica
disponível para as funções da Vercel. Depois de criar o banco, aplique as migrations
com `alembic upgrade head` usando uma conexão configurada para esse banco antes de
usar a aplicação. Para previews em domínios diferentes, configure `ORIGEM_FRONTEND`
no ambiente Preview com a origem correspondente.

O deploy não cria automaticamente as contas de demonstração nem migra o banco.
Essas tarefas devem ser executadas separadamente contra o PostgreSQL hospedado.

O banco é o **PostgreSQL**, e ele precisa existir antes do back subir. O caminho usado hoje é um
banco do Supabase, configurado no `.env` da **raiz** do repositório (o `configuracao.py` lê esse
arquivo, não o `backend/.env`). O desenho dele mora nos modelos, em `backend/modelos/`, e nas
migrations em `backend/migracoes/versions/`.

```bash
cd backend
python criar_tabelas.py
```

O `criar_tabelas.py` executa `alembic upgrade head`: cria as tabelas e carrega os grupos e as
permissões iniciais. Ele pode ser executado de novo para aplicar só o que falta. Um banco local
também funciona; nesse caso preencha `BANCO_HOST`, `BANCO_PORTA`, `BANCO_NOME`, `BANCO_USUARIO` e
`BANCO_SENHA` no `.env` da raiz.

> O `docker-compose.yml` da raiz ainda descreve um MySQL 8.4 e variáveis `BANCO_*` de outro
> momento do projeto. A API atual usa PostgreSQL/Supabase e não se conecta a esse serviço MySQL;
> o Compose não é o caminho de execução recomendado.

Depois, prepare o ambiente do Python e instale as dependências do `requirements.txt`:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

O `requirements.txt` contém as dependências da API, incluindo FastAPI, SQLAlchemy,
o driver PostgreSQL e Alembic.

E aí o back sobe:

```bash
fastapi dev main.py
```

Com o back no ar, o esperado é:

- o terminal mostrar `http://localhost:8000`;
- abrir `http://localhost:8000/docs` e ver as rotas principais e administrativas da API;
- fazer login em `/autenticacao/login` e enviar o token Bearer em `Authorization` para acessar
  as rotas de usuários, tatuagens, passos, imagens, agenda e grupos.

A raiz `http://localhost:8000` responde `{"status":"ok"}` para confirmar que o back está no ar,
sem consultar o banco.

O `.env` precisa ter `ORIGEM_FRONTEND` com o endereço exato do front, porque é dele que sai o CORS.
Se o endereço mudar, mude no `.env` e reinicie o back.

### Redefinir senha

Na tela de entrada, use **Esqueci minha senha**. A API envia um link ao email cadastrado; o link
vence em 15 minutos e só pode ser usado uma vez. A tela pede a nova senha duas vezes. Para trocar
a senha já conectado, use **Alterar senha** e informe a senha atual.

O envio exige as variáveis `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` e
`SMTP_FROM_EMAIL` no ambiente do backend. No ambiente local, coloque-as no `.env` da raiz; na
Vercel, configure-as no projeto Backend. O link usa `ORIGEM_FRONTEND`, que deve apontar para a URL
da tela. Depois de atualizar um banco existente, aplique a nova migration com `alembic upgrade head`.

### As contas de demonstração

Quem entra no sistema é uma **conta**, e a conta mora na tabela `usuarios`, com o papel dela
escrito no banco: `cliente`, `tatuador` ou `administrador`. As contas de demonstração são criadas
por um script. O cadastro público também existe, mas só cria Cliente; o papel Tatuador é atribuído
pelo estúdio, e Administrador é provisionado por comando local:

```bash
cd backend
python criar_contas_de_demonstracao.py
```

| conta | e-mail | senha | papel | o que ela vê |
| --- | --- | --- | --- | --- |
| Bruna | `bruna@tracofino.com.br` | `bruna123` | cliente | "Pedir tatuagem" e "Minhas tatuagens" |
| Vitor | `vitor@tracofino.com.br` | `vitor123` | tatuador | "A agenda" e "A ficha" |
| Waldemar | `waldemarroberto.kuehn@gmail.com` | a de sempre | administrador | administrador do sistema |

A conta da Bruna fica ligada à cliente 1 da tabela `clientes`, que é a mesma pessoa: por isso ela
enxerga as cinco tatuagens da Bruna. A conta do Vitor não tem cliente nenhuma, porque tatuador não é
dono de tatuagem. Ao repetir o script, contas de demonstração já existentes são preservadas; a
conta do dono é promovida para Administrador sem trocar a senha. Para corrigir essa conta num banco
que já existe, use `python promover_administrador.py` dentro de `backend/`.

No cadastro público, depois que `POST /usuarios` confirma a criação, a tela volta para o formulário
de login com o email preenchido. Ela não autentica automaticamente. O link **Esqueci minha senha**
envia um token por email, válido por 15 minutos e de uso único; o banco guarda somente o hash do
token. A resposta da API não revela se o endereço está cadastrado. A opção **Alterar senha** pede a
senha atual e a confirmação da nova senha.

Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` e `SMTP_FROM_EMAIL` somente no
ambiente do backend. `ORIGEM_FRONTEND` define o endereço usado no link. Sem SMTP, a recuperação
responde que o recurso não está configurado. Depois de atualizar um banco existente, rode
`alembic upgrade head` para incluir os campos do token.

O login devolve um **token Bearer** e os dados públicos da conta; o front guarda o token na sessão
da aba e escolhe a tela pelo papel retornado pelo back. Nas requisições protegidas, envia o token
em `Authorization: Bearer ...`. A rota `/usuarios/eu` também permite consultar o perfil da sessão.
O front não tem nenhum id de usuário escrito no código.

O cadastro `POST /usuarios` é público e sempre cria uma conta Cliente; depois do sucesso, a pessoa
precisa entrar com email e senha. As demais operações protegidas verificam permissões do grupo no
banco a cada requisição, incluindo o acesso às tatuagens e aos passos próprios. As rotas de gestão
de grupos são exclusivas do Administrador.
O catálogo pode ser consultado em `GET /grupos/permissoes`; o Administrador lista e cria grupos,
troca permissões e atribui contas a grupos pela API. O primeiro Administrador pode ser criado
localmente com `python criar_administrador.py`, depois das migrations, e a senha é solicitada sem
eco no terminal. `python promover_administrador.py` altera apenas o papel da conta do administrador
já identificada no projeto.

## Mudança no banco: migrations

O banco é o PostgreSQL, e o desenho dele mora nos modelos, em `backend/modelos/`. O problema do
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

O histórico de migrations já existe em `migracoes/versions/`. A migration `20261106_01` acrescenta
à tabela `usuarios` os campos que guardam o hash e os horários do link temporário de redefinição.
Em uma instalação existente, `alembic upgrade head` aplica essa migration antes de usar a
recuperação de senha. Não altere o banco manualmente: mudança de modelo deve ser versionada.

Conferindo o estado sem escrever nada: `alembic check` responde `No new upgrade operations detected`
quando o banco bate com os modelos.

## Como rodar o front

O front é o React, na pasta `frontend/`. Ele precisa do back no ar, porque as telas de trabalho
chamam a API. Só React e React DOM são dependência de execução: não há biblioteca de rotas, nem de
requisição. As telas da cartilha e as telas de apoio usam o estado do `App.jsx`.

```bash
cd frontend
npm install
npm run dev
```

O esperado é o Vite abrir `http://localhost:5173` e a tela de login aparecer. Entre com uma das
contas de demonstração, que estão na tabela de contas do back: Bruna entra como Cliente, Vitor como
Tatuador e Waldemar como Administrador. Esse endereço tem que ser igual ao `ORIGEM_FRONTEND` do
`.env` da raiz, senão o navegador bloqueia a chamada por CORS.

As telas estão escritas. Escolhendo Bruna, "Minhas tatuagens" mostra as cinco tatuagens dela, com a
etapa de cada uma, o histórico ao clicar em "Ver histórico", as imagens e a agenda; "Pedir
tatuagem" grava no back e volta com a etapa `pedida`. Escolhendo Vitor, "A agenda" lista as oito
tatuagens do estúdio com filtro por etapa e miniatura do desenho, e "Abrir ficha" abre uma delas
para registrar passos, enviar o desenho e marcar sessões ou o retoque. Waldemar recebe a tela
"Administração", onde cadastra tatuadores e atribui o responsável de cada tatuagem. A ficha mostra
os resultados da regra do back: quando aceita, a etapa nova aparece; quando recusa, o motivo aparece
e a etapa não muda.

### A cara da tela

A entrada tem a foto do ateliê e uma vitrine. Na barra, cada conta é identificada pelas iniciais do
próprio nome e pelo papel retornado pelo backend; as fotos de Bruna e Vitor não são usadas como
avatar de outras pessoas. A barra reúne logo, plaquinha do estúdio, identidade da conta e botão de
tema. O Administrador recebe a tela de administração; Cliente e Tatuador veem as telas do próprio
papel. Cada tatuagem ganha a linha do tempo das quatro etapas e o histórico registra cada passo.

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
- Os dados ficam no PostgreSQL, e o desenho do banco mora nos modelos, em `modelos/`. A conexão
  nasce no middleware de `main.py`, é guardada por requisição e chega aos repositórios por
  `banco.cursor()`.
- Mudança numa tabela que já existe é migration, em `migracoes/versions/`, versionada no Git. Nunca
  `DROP TABLE` e nunca `ALTER TABLE` escrito à mão.
- A regra da cartilha mora no serviço. Quando ela recusa, o serviço devolve `None` ou o motivo, e
  é a rota que escolhe o status.
- `async def` não entra. Rota é `def` normal.
- CORS liberado só para o endereço do front, lido do `.env`. Nunca `["*"]`.
- O login usa token Bearer, armazenado na sessão da aba. O grupo e suas permissões moram no banco,
  e é o back que os devolve: o front não tem id de usuário escrito no código.
- A conta é uma tabela só dela, e a cliente continua na tabela `clientes`. A ligação é a coluna
  `usuarios.cliente_id`, e ela é vazia para o tatuador, que não é dono de tatuagem nenhuma.
- Cadastro de Cliente e login são públicos; as demais rotas aplicam permissões de grupo no servidor.
- Cor mora em token, em `estilos/tokens.css`. Nenhuma tela escreve um código de cor, e nenhum
  hexadecimal sobrou no CSS: até o branco do botão principal é `--cor-sobre-acento`.
- A marca não é duplicada no front, e a fonte não vem de link. As duas coisas vêm do repositório.
