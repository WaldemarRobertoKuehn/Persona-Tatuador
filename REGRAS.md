# Regras do projeto para a IA

Atualizado até a **aula 3** da UC2, Práticas DevOps em Projetos Web. Salve na raiz do repositório
da cartilha com o nome `REGRAS.md`, por cima da versão da UC4. Só vale a versão mais nova.

O estado atual inclui melhorias solicitadas depois da aula: cadastro público de clientes sem login
automático, recuperação e troca de senha, perfis distintos de Cliente, Tatuador e Administrador,
identificação visual por iniciais da conta, imagens de referência e desenho, agenda por tatuador
responsável e tela de Administração. Essas funcionalidades já fazem parte do projeto e não devem ser
tratadas como propostas pendentes.

## O projeto

- Repositório da cartilha sorteada na UC4. Na UC2, ele é o caso que vai para produção: a aplicação
  foi desenvolvida na UC4. Agora vamos preparar a infraestrutura e a publicação.
- Na raiz: `README.md`, `REGRAS.md`, `docs/` (a cartilha, o briefing, o DER, o COMO_RODAR e a
  arquitetura), `.docs/` (o diário de obra), `frontend/`, `backend/`, `api/` e os arquivos de deploy.
- A infraestrutura real é **Vercel + Supabase**: o React é estático na Vercel, a API roda como função
  serverless e o banco é um PostgreSQL do Supabase. O `.env` fica na raiz e o `configuracao.py` é o
  único que o lê. O `docker-compose.yml` é legado: ele ainda declara MySQL 8.4, `banco`, `api` e
  `web`; não é o caminho de produção nem prova que a API atual se conecta a esse MySQL.
- `Caddyfile` na raiz: do caminho local com contêineres. Atende na porta 80, entrega o `/srv` e
  encaminha `/api/*` para `api:8000`, tirando o prefixo `/api`.
- `backend/Dockerfile`, `backend/.dockerignore` e `backend/requirements.txt`, gerado com `pip freeze`.
- `frontend/Dockerfile`, em duas etapas (Node para o build, Caddy com o `dist/`), e `frontend/.dockerignore`.
- `frontend/`: o React, rodando com `npm run dev` na porta 5173. O endereço da API vem da variável
  `VITE_URL_DA_API`, lida em `src/api.js`: `.env.development` tem o endereço local que o projeto já usa (no exemplo,
  `http://localhost:8000`) e
  `.env.production` tem `/api`. Os dois arquivos vão para o Git e não têm segredo.
- `frontend/dist/`: gerado pelo `npm run build`, fora do Git.
- `backend/`: a API em FastAPI, em camadas (`rotas/`, `servicos/`, `repositorios/`, `esquemas/`,
  `modelos/`), com PostgreSQL pelo SQLAlchemy/psycopg2, migrations com Alembic e login com JWT. Fora do Docker, roda com
  `fastapi dev main.py`. No contêiner, usa `fastapi run main.py --port 8000`.
- `api/index.py` e `vercel.json` na raiz: o deploy que serve o front e a API no mesmo projeto da
  Vercel. `backend/vercel.json` e `backend/api/index.py` fazem o mesmo para o projeto separado de API.
- `.docs/` contém os registros de IA e infraestrutura mantidos no repositório, incluindo `ia.md`,
  `infra.md` e `proximos-passos.md`.
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
- IaaS, PaaS e SaaS como modelos. EC2, SSH com chave `.pem`, o domínio apontando para o IP e o Caddy
  emitindo o certificado após configurar domínio, DNS e portas: vistos na demonstração do professor, opcionais.

## Funcionalidades implementadas depois da aula

- O cadastro público `POST /usuarios` cria somente contas Cliente. Depois do cadastro, a tela volta
  ao login; criar uma conta não inicia uma sessão.
- O login retorna o token e os dados públicos do perfil. Cliente, Tatuador e Administrador recebem
  telas e rótulos próprios; a autorização continua sendo decidida pelos grupos e permissões do backend.
- A recuperação de senha envia um link por SMTP. O token expira em 15 minutos, só pode ser usado
  uma vez e é persistido como hash. A troca autenticada exige a senha atual; as duas operações
  confirmam a nova senha.
- O envio de email depende de `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` e
  `SMTP_FROM_EMAIL`, configurados somente no ambiente do backend.
- A conta do Administrador tem painel próprio. `backend/promover_administrador.py` promove a conta
  existente identificada pelo projeto; o script de demonstração mantém esse papel ao ser repetido.
- A barra usa iniciais do nome retornado pelo backend. As imagens das personas de demonstração não
  são mais avatares compartilhados entre todas as contas.
- `backend/migracoes/versions/20261106_01_tokens_redefinicao_senha.py` adiciona os campos de
  expiração e hash do token. O banco existente precisa receber essa migration antes de usar a recuperação.
- Há testes unitários focados na redefinição em `backend/tests/`; eles não substituem testes de integração
  com banco ou provedor SMTP.
- As imagens de uma tatuagem ficam na tabela `tatuagem_imagens`, em `BYTEA`, com limite de 4 MB e
  tipos JPEG, PNG e WebP. O cliente envia referência e aprova ou recusa o desenho; o tatuador envia o
  desenho. A aprovação do desenho na etapa `pedida` registra o passo e move a etapa.
- A agenda é do tatuador responsável, em blocos de uma hora, no fuso UTC-3. Sábado tem expediente
  reduzido e domingo é fechado. Um índice único parcial impede dois agendamentos ativos no mesmo
  horário do mesmo tatuador; cancelar libera o horário sem apagar o histórico.
- `tatuagens.tatuador_id` é o responsável pela agenda, atribuído pelo Administrador. A migration
  `20261107_02` criou a coluna; o modelo ORM de `tatuagens` ainda não a declara, e o repositório a
  acessa por SQL explícito.
- A tela **Administração** cadastra tatuadores e atribui o responsável de cada tatuagem. A gestão de
  grupos e permissões continua disponível pelas rotas `/grupos` e `/usuarios/{id}/grupo`.
- Há testes unitários de agenda, imagem e tatuador em `backend/tests/`, além dos de redefinição.

## O que ainda não foi visto, e não deve aparecer

- Mudanças adicionais na lógica do backend além das funcionalidades implementadas e registradas
  nesta seção, salvo quando forem solicitadas explicitamente. Mudanças em tabelas continuam exigindo
  migrations versionadas; não altere o banco manualmente.
- Redes do Docker declaradas à mão, `network_mode: host`, Docker Swarm e Kubernetes.
- Nginx configurado no projeto. Ele só foi mostrado para comparar.
- Domínio e HTTPS no `Caddyfile` do repositório. Isso só existe no servidor da demonstração.
- Scripts `.sh` e `Makefile`.
- Branches, pull request, tags e proteção da `main`. O Git continua como na UC4.
- GitHub Actions e pipeline de CI/CD. Os testes unitários existentes devem continuar passando.
- Ferramenta de monitoramento, logs centralizados, métricas.

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
  de uma requisição e o que ainda está chumbado no código.
- Escreva frases curtas. Marque com `?` o que você deduziu sem confirmar no código.
- Não leia `.env` do backend ou da raiz, chaves privadas ou credenciais. Consulte `.env.exemplo`, se existir.
  No front, leia ou altere apenas `VITE_URL_DA_API` nos arquivos de variáveis desta aula.
  Não copie outros valores para a resposta ou para a documentação.
- Nunca escreva senha, chave do `.env`, token ou IP de servidor real na `.docs/` nem no README.

## Como responder

- Uma coisa por vez. Não adiante etapa que eu não pedi.
- Se a tarefa exigir algo da lista de cima, avise antes e proponha a versão simples.
- Em todo desenho, diga onde cada peça roda. Para servidores, indique as portas e o acesso
  público ou interno. Para o navegador, indique que é cliente. Não invente uma porta pública nele.
- Quando houver mais de uma escolha de infraestrutura, me mostre as opções e o que cada uma custa.
  A escolha é minha.
- Justifique cada decisão em uma linha. Eu preciso explicar o que entrego na apresentação.
- Não apague bancos, volumes ou backups. Não execute `docker compose down -v`.
