# Regras do projeto para a IA

Regras até a aula 2 da UC3, Desenvolvimento de Software Apoiado por IA. Salvar na raiz do
repositório da cartilha como `REGRAS.md`, substituindo a versão anterior.

## O projeto

- Repositório da cartilha sorteada na UC4. A aplicação foi desenvolvida na UC4 e publicada na UC2.
  Na UC3, ela ganha a funcionalidade de IA planejada no `.docs/ia.md` e apresentada na avaliação.
- As chaves da IA ficam no `backend/.env`: `GEMINI_API_KEY` e `OPENROUTER_API_KEY`, grátis, e
  `ANTHROPIC_API_KEY`, paga, do professor. O `configuracao.py` lê com `chave_do_gemini`,
  `chave_do_openrouter` e `chave_do_claude`. O `.env.exemplo` tem os três nomes, sem valor.
- `backend/testar_ia.py`: o primeiro pedido, direto pela API do Google, fora da API do projeto.
- `backend/testar_jangada.py`: o mesmo pedido pelo Jangada (`jangada-ai`), uma biblioteca que chama
  os provedores, e o pedido do `.docs/ia.md` com a instrução de sistema. Os dois scripts servem
  para testar antes de integrar a funcionalidade.
- `backend/ia/`: a pasta da funcionalidade de IA. As configurações dos provedores e as tools ficam aqui.
  A rota chama uma função dessa pasta.
  - `ia/__init__.py`, vazio.
  - `ia/modelos.py`: o `gemini` (principal, plano grátis), o `openrouter` (`openrouter/free`, a
    primeira reserva, grátis), o `claude` (a terceira opção, chave paga do professor) e
    `llm = gemini.with_fallback(openrouter, claude)`, que o projeto usa.
  - `ia/ferramentas.py`: as tools da funcionalidade, prontas do Jangada ou funções do projeto, e a
    lista `FERRAMENTAS`.
  - `ia/<funcionalidade>.py`: a `INSTRUCAO` e a função que monta a entrada e chama a IA, com um
    `Agent` quando houver tools.
- A rota da funcionalidade chama a função da `ia/`, com `POST`, não grava nada sem a pessoa conferir e
  devolve 503 com uma frase quando nenhuma das três opções responde.
- Na raiz: `README.md`, `docs/` (a cartilha, o briefing e o DER), `.docs/` (o diário de obra),
  `frontend/` e `backend/`.
- Em produção: o banco é o PostgreSQL do Supabase, pelo Transaction pooler (porta 6543). A API e a
  tela são dois projetos na Vercel, do mesmo repositório: a API com Root Directory `backend`, a tela
  com Root Directory `frontend`. O `frontend/vercel.json` encaminha `/api/:caminho*` para a API. As
  senhas ficam nas Environment Variables da Vercel e no `backend/.env`, nunca no Git.
- `backend/banco.py`: o `create_engine` usa `poolclass=NullPool`, porque quem guarda conexões é o pooler.
- `backend/main.py` liga o Sentry antes de criar o `app`. O DSN vem da variável `DSN_DO_SENTRY`.
- `docker-compose.yml` na raiz, com três serviços: `banco` (MySQL 8.4, com o volume
  `dados_do_banco`), `api` (imagem do `backend/Dockerfile`) e `web` (imagem do `frontend/Dockerfile`,
  com o Caddy acessível pela porta 8080 da máquina). As senhas vêm do `.env` da raiz, que fica fora do Git; o `.env.exemplo`
  tem as mesmas chaves, sem valor.
- `Caddyfile` na raiz: o servidor web. Atende na porta 80 do contêiner, entrega o `/srv` e encaminha
  `/api/*` para `api:8000`, tirando o prefixo `/api`.
- `backend/Dockerfile`, `backend/.dockerignore` e `backend/requirements.txt`, gerado com `pip freeze`.
- `frontend/Dockerfile`, em duas etapas (Node para o build, Caddy com o `dist/`), e `frontend/.dockerignore`.
- `frontend/`: o React, rodando com `npm run dev` na porta 5173. O endereço da API vem da variável
  `VITE_URL_DA_API`, lida em `src/api.js`: `.env.development` tem o endereço local que o projeto já usa (no exemplo,
  `http://127.0.0.1:8000`) e
  `.env.production` tem `/api`. Os dois arquivos vão para o Git e não têm segredo.
- `frontend/dist/`: gerado pelo `npm run build`, fora do Git.
- `backend/`: a API em FastAPI, em camadas (`rotas/`, `servicos/`, `repositorios/`, `esquemas/`,
  `modelos/`), com SQLAlchemy, migrations com Alembic e login com JWT. O Compose local usa MySQL;
  a publicação desta aula usa PostgreSQL no Supabase. Fora do Docker, roda com
  `fastapi dev main.py`. No contêiner, usa `fastapi run main.py --port 8000`. O MySQL roda na porta 3306.
- `.docs/` tem `README.md`, `arquitetura.md`, `decisoes.md`, `proximos-passos.md`, `roadmap.md`
  e `ia.md`, mais o `infra.md`, com a arquitetura de produção e a seção "Como saber que caiu", e a
  pasta `prints/`.
- Trabalho individual, inclusive o desenho de abertura. Cada aluno usa o próprio projeto e repositório.
- Código, nomes, comentários, documentação e respostas sempre em português do Brasil.
- Cartilha: escreva aqui o número e o nome, e em uma linha a pessoa e a regra.

## O que já foi visto, e pode usar

- Tudo o que a UC4 ensinou e já está no código do projeto. Leia o código antes de supor.
- Cliente e servidor: o servidor recebe pedidos em uma porta; o cliente inicia a comunicação.
- IP, porta, `localhost` e `127.0.0.1`, `0.0.0.0`, DNS e domínio, HTTP na porta 80 e HTTPS na 443.
- O React roda no navegador de quem abre a tela. O Vite só entrega os arquivos.
- `fastapi dev main.py --host 0.0.0.0` e `npm run dev -- --host`, só para testar na rede do laboratório.
- Os comandos `ipconfig`, `ip -4 addr` e `nslookup`, e a aba Rede do navegador.
- Ambiente de desenvolvimento e de produção, e o que muda entre eles: endereço da API, tela,
  banco, `.env` e CORS.
- Na arquitetura: servidor web como recepção, CDN, balanceador, réplica de banco e monitoramento,
  só como nomes de peças num desenho.
- Mermaid: `flowchart LR`, caixas com `apelido[texto]`, setas `-->|texto|` e cilindro `[(texto)]`
  para banco. No Markdown, use abertura ```mermaid e fechamento ```. No Mermaid Live, cole
  só o conteúdo, começando em `flowchart LR`.
- No desenho da aula, o servidor web recebe HTTPS na 443 e encaminha `/api` à API interna
  na 8000. O banco atende internamente na 3306. É uma proposta, não uma regra para todo site.
- A imagem reúne os arquivos do programa e suas dependências. O contêiner é uma instância
  isolada que compartilha o núcleo do sistema. Dados de banco exigem armazenamento próprio.
- Docker: o que é imagem e contêiner, Docker Hub, `docker --version`, `docker run hello-world`,
  `docker images` e `docker ps -a`. A instalação do Docker Desktop com WSL 2.
- `npm run build` e a pasta `dist/`. Variáveis do Vite: `.env.development`, `.env.production`, o
  prefixo `VITE_` e `import.meta.env`. Variável `VITE_` vai para o navegador: nunca leva segredo.
- Servidor web: entregar arquivos, proxy reverso e HTTPS, como papéis. Nginx e Caddy comparados.
- Caddy: `Caddyfile` com `:80`, `handle_path`, `reverse_proxy`, `handle`, `root` e `file_server`.
- `docker run --rm -p 8080:80 -v origem:destino caddy:2`, e `host.docker.internal` para o contêiner
  chegar à API, que sobe com `--host 0.0.0.0`.
- Mesma origem: mesmo protocolo, endereço e porta. Na mesma origem, o navegador não aplica CORS.
- `pip freeze > requirements.txt`, com o venv ativo.
- `Dockerfile` com `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`, e o build em duas etapas com `AS` e
  `COPY --from`. `.dockerignore`.
- `docker compose` com `services`, `image`, `build`, `environment`, `ports`, `volumes`, `depends_on`,
  variáveis `${...}` lidas do `.env` da raiz e volume nomeado.
- Na rede padrão do Compose, os serviços se encontram pelo nome: `banco:3306`, `api:8000`.
- O `depends_on` simples controla a ordem de partida. Ele não espera o MySQL aceitar conexões.
- `docker compose up -d --build`, `ps`, `logs`, `exec`, `down`. O `down -v` apaga o volume do banco.
- `fastapi run` como o modo de produção do FastAPI.
- Supabase: projeto, região, senha do banco, botão Connect, Direct connection, Session pooler e
  Transaction pooler, Table Editor e RLS ativo em cada tabela, sem políticas. A conexão direta
  com o usuário `postgres` ignora o RLS; a API da aplicação continua responsável pelas permissões.
- PostgreSQL com o driver `psycopg2-binary` e a URL `postgresql://`. `NullPool` no `create_engine`.
- Vercel: projeto importado do GitHub, Root Directory, Environment Variables, Deploy, Redeploy, Logs,
  Domains e o deploy integrado ao Git. Na configuração padrão, a branch de produção atualiza o site
  após um deploy bem-sucedido; outras branches geram prévias. `vercel.json` com
  `rewrites`. Função sem servidor: execução sob demanda e sem garantia de arquivos locais persistentes.
- Vercel e Supabase administram os servidores. O aluno configura a aplicação, o banco e o domínio
  pelos painéis das plataformas. A publicação da aula 4 parte do projeto local com Docker Compose.
- Log: o registro que o programa escreve enquanto roda. O terminal do `fastapi dev` já era um log.
  A linha de acesso traz endereço, método, caminho e status. O erro 500 deixa um traceback, que se
  lê de baixo para cima: a última linha diz o tipo do erro e a mensagem.
- `docker compose logs api`, com `--tail N` para as últimas linhas e `-f` para acompanhar.
  `docker compose stop banco` e `docker compose start banco` para derrubar e religar um serviço.
- Logs da API na Vercel, na aba Logs do projeto. No plano Hobby, o log de execução fica guardado
  por uma hora.
- A rota `/health` como sinal de vida. Do jeito que está, ela prova que a API respondeu, e não que
  o banco está de pé.
- Sentry como o log de produção dos erros, no plano grátis Developer. O `sentry-sdk` no
  `requirements.txt`; `dsn_do_sentry = os.getenv("DSN_DO_SENTRY")` no `configuracao.py`; no
  `main.py`, `import sentry_sdk` e o `sentry_sdk.init` antes do `app = FastAPI(...)`, com
  `dsn=configuracao.dsn_do_sentry`, `include_local_variables=False` e `max_request_body_size="never"`.
  Sem essas duas opções, um erro no login manda a senha e o e-mail para o Sentry.
- O DSN fica só nas Environment Variables do projeto da API na Vercel. No `.env.exemplo`, a chave vai
  sem valor. Sem DSN, o Sentry fica desligado: no computador, ele não envia nada.
- A rota temporária `GET /erro-de-teste`, com `1 / 0`, serviu para forçar o erro em produção e foi
  apagada depois do teste. Ela não volta.
- O projeto grátis do Supabase pausa depois de 7 dias sem pedidos ao banco. Ele volta pelo painel.

- UC3, aula 1: o modelo de linguagem gera texto a partir do pedido recebido. Neste teste, ele não
  acessa o banco do projeto. Pode errar com confiança e variar a resposta à mesma entrada.
- Chat e API: no chat, uma pessoa digita; na API, o programa manda o pedido com a chave e recebe a
  resposta como dado. A API do projeto passa a ser cliente da API do Google.
- As peças do pedido: modelo, instrução de sistema (o papel e as regras, fixos), entrada (o caso de
  agora, que muda) e resposta.
- `from google import genai`, `genai.Client(api_key=configuracao.chave_do_gemini)` e
  `cliente.interactions.create(model=..., system_instruction=..., input=...)`, com a resposta em
  `.output_text`. O modelo da aula é o `gemini-3.8-flash`.
- Os erros: sem chave, `ValueError` (`No API key was provided`); chave errada, 400
  (`API key not valid`); limite do plano grátis, 429 (`RESOURCE_EXHAUSTED`). O limite vale por projeto.
- O plano grátis: o Google usa as entradas e as respostas para melhorar os produtos, e pessoas podem
  ler. Só dados fictícios nos pedidos.

- O AI Studio: a área de testes (Playground), o **Get code** e a página de limites do projeto.
- O OpenRouter: uma porta para muitos modelos com uma chave só. Os modelos grátis têm limite (sem
  créditos comprados, 20 pedidos por minuto e 50 por dia), e o `openrouter/free` escolhe um deles.
  Alguns provedores grátis guardam os pedidos: só dados fictícios.

- UC3, aula 2: `pip install -U google-genai "jangada-ai[gemini,openai,anthropic]"`. O `[openai]` é o
  que o Jangada usa para falar com o OpenRouter.
- Jangada: `from jangada_ai import LLM`,
  `LLM("gemini", "gemini-3.8-flash", api_key=configuracao.chave_do_gemini)`,
  `llm.complete(entrada, system=INSTRUCAO)` e a resposta em `.text`, com `.provider` e `.model`
  dizendo quem respondeu.

- Fallback em três níveis: `gemini.with_fallback(openrouter, claude)`. O Jangada tenta de novo no limite
  (429), na demora, na falha de conexão e no erro 5xx, e depois passa ao próximo; no modelo inexistente
  (404) passa direto. Chave inválida e pedido errado dão erro, sem passar adiante. A espera soma a cada
  nível. `resposta.provider` diz quem respondeu.
- Tools: uma função que a IA pode pedir para o código rodar. Prontas do Jangada
  (`jangada_ai.prebuilt`: `consultar_cep`, `feriados_nacionais`, `wikipedia_search`, `calculator` e
  outras), nativas do provedor (`web_search()`, que no Gemini é a busca do Google) e funções do
  projeto, com tipos e docstring. `Agent(llm, role=..., goal=INSTRUCAO, tools=[...]).run(entrada)` faz
  o laço e devolve `.text`.
- Tool só lê ou calcula. Ela não grava, não apaga e não manda nada para fora sem a pessoa conferir.

## O que ainda não foi visto, e não deve aparecer

- Chamada à IA pelo `frontend/`, SDK de provedor no `frontend/` e qualquer chave em variável `VITE_`.
- Código de IA fora da pasta `backend/ia/`, e provedor chamado sem passar pelo `llm` de `ia/modelos.py`.
- Streaming, conversa com memória, vários agentes (`Squad`, `Flow`, `Graph`), MCP e RAG.
- `async def` e cliente assíncrono.
- LangChain, LlamaIndex, CrewAI e outro orquestrador no lugar do Jangada.
- Gravar no banco o que a IA devolveu sem uma pessoa conferir antes.
- Mudança na regra da cartilha, nos modelos e nas migrations por causa da IA.
- Redes do Docker declaradas à mão, `network_mode: host`, Docker Swarm e Kubernetes.
- Nginx configurado no projeto. Ele só foi mostrado para comparar.
- Domínio e HTTPS no `Caddyfile` do repositório. Nesta aula, domínio e certificado são configurados
  pela Vercel. O Caddy continua no ambiente local.
- SDK do Supabase, API REST do Supabase, autenticação do Supabase e regras de RLS escritas à mão.
- `asyncpg`, `psycopg` 3, `async def` e sessão assíncrona.
- Vercel Services, `builds` e `routes` no `vercel.json`, e `vercel.json` no `backend/`.
- Scripts `.sh` e `Makefile`.
- Branches, pull request, tags e proteção da `main`. O Git continua como na UC4.
- GitHub Actions e testes automatizados. A entrega contínua é a da Vercel, a cada push.
- Código novo de log no `backend/` (`logging`, `print` de depuração esquecido no código entregue).
- `send_default_pii`, `traces_sample_rate`, profiling e logs do Sentry. Só os erros.
- SDK do Sentry no `frontend/`.
- Monitor externo de disponibilidade, métricas, painéis, Grafana, Prometheus e afins.
- `healthcheck` no `docker-compose.yml` e mudança na rota `/health`.
- Agendador para manter o Supabase acordado (cron, GitHub Actions ou similar).

## Como escrever o código

- Todo código que você gerar vem comentado em português. Um comentário curto acima de cada rota,
  função ou bloco, dizendo o que ele faz e por que está ali.
- O comentário explica a intenção. Não repita o que a linha já diz: `# retorna a lista` em cima
  de `return lista` não ensina nada.
- Na primeira vez que aparecer algo novo para mim (um decorador, um tipo, um parâmetro), explique
  em uma linha, no próprio comentário.
- Os comentários ficam no código que eu entrego. É por eles que eu estudo antes da apresentação.
- Depois do código, escreva um resumo curto: quais arquivos você criou ou alterou, o que mudou em
  cada um e como eu testo, com a URL ou o comando e o que deve aparecer na tela.

## Como manter a .docs/

- No começo de toda conversa, leia a `.docs/` inteira antes de abrir qualquer outro arquivo.
- O que é infraestrutura vai no `infra.md`: o desenho de produção, a tabela de ambientes, o caminho
  de uma requisição, o que ainda está chumbado no código e onde olhar quando algo cai.
- Escreva frases curtas. Marque com `?` o que você deduziu sem confirmar no código.
- Não leia `.env` do backend ou da raiz, chaves privadas ou credenciais. Consulte `.env.exemplo`, se existir.
  No front, leia ou altere apenas `VITE_URL_DA_API` nos arquivos de variáveis desta aula.
  Não copie outros valores para a resposta ou para a documentação.
- Nunca escreva senha, chave do `.env`, token ou IP de servidor real na `.docs/` nem no README.

## Como responder

- Uma coisa por vez. Não adiante etapa que eu não pedi.
- Nas instruções de passo a passo, use verbos no infinitivo.
- Se a tarefa exigir algo da lista de cima, avise antes e proponha a versão simples.
- Em todo desenho, diga onde cada peça roda. Para servidores, indique as portas e o acesso
  público ou interno. Para o navegador, indique que é cliente. Não invente uma porta pública nele.
- Quando houver mais de uma escolha de infraestrutura, me mostre as opções e o que cada uma custa.
  A escolha é minha.
- Justifique cada decisão em uma linha. Eu preciso explicar o que entrego na apresentação.
- Num trecho de log que eu colar, se aparecer senha, token ou e-mail de usuário, me avise para apagar
  e não repita o valor na resposta.
- Não apague bancos, volumes ou backups. Não execute `docker compose down -v`.
