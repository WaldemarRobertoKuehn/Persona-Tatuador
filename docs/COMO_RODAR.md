# Como rodar e como fechar

Este arquivo é o passo a passo do dia a dia: o que fazer para abrir o projeto e o que
fazer para fechar. Os dois servidores são processos que ficam rodando até serem
parados, e é por isso que o site continua respondendo no navegador depois de você
fechar a aba.

## O que precisa existir na máquina

- **PostgreSQL do Supabase**, para o banco. Configure `SUPABASE_DB_URL`,
  `SUPABASE_DB_PASSWORD` e `BANCO_SSLMODE` no `.env` da **raiz** do repositório,
  que é o arquivo que o `backend/configuracao.py` lê.
- **Python**, para o back. O `venv` já está criado em `backend/venv`, então não é
  preciso instalar nada: é só ativar.
- **Node.js**, para o front. O `node_modules` já está em `frontend/`, então
  `npm install` só é preciso se você apagar essa pasta.

### Configurar a IA

Configure `GEMINI_API_KEY` e `OPENROUTER_API_KEY` no `.env` da raiz. A chave
`ANTHROPIC_API_KEY` é opcional e habilita o último provedor de reserva.

Se estiver usando o Compose legado, as três variáveis são repassadas para a API
pelo `docker-compose.yml`. Depois de alterar o `.env`, recrie o serviço `api`
para ele receber os valores novos:

```powershell
docker compose up -d --build --force-recreate api
```

### Se o banco não existir ainda

O back não sobe sem o PostgreSQL, porque é nele que os dados moram. O desenho do
banco mora nos modelos e nas migrations em `backend/migracoes/`. Configure o
`.env` da raiz com os dados de conexão do Supabase e aplique as migrations:

```powershell
cd backend
python criar_tabelas.py
```

O script executa `alembic upgrade head`, criando as tabelas e carregando os
grupos e permissões iniciais. Ele pode ser executado novamente para aplicar
somente as migrations que ainda faltam.

### Se as contas de demonstração não existirem

Quem entra no sistema é uma conta da tabela `usuarios`, e elas são criadas por
um script, e não pela tela:

```powershell
cd backend
python criar_contas_de_demonstracao.py
```

| conta | e-mail | senha | papel |
| --- | --- | --- | --- |
| Bruna | `bruna@tracofino.com.br` | `bruna123` | cliente |
| Vitor | `vitor@tracofino.com.br` | `vitor123` | tatuador |
| Waldemar | `waldemarroberto.kuehn@gmail.com` | a de sempre | administrador |

O script pode rodar de novo sem quebrar nada: conta que já existe é pulada, e a
senha de quem já tem conta não muda.

### Criar o primeiro Administrador

Depois de aplicar as migrations, rode o comando local no diretório `backend`.
Ele cria a primeira conta no grupo Administrador e solicita a senha sem exibi-la
nem colocá-la nos argumentos do comando:

```powershell
cd backend
python criar_administrador.py
```

A conta Administrador entra na tela **Administração**, onde cadastra tatuadores
(`POST /usuarios/tatuadores`) e atribui o tatuador responsável por cada tatuagem
(`PUT /tatuagens/{tatuagem_id}/tatuador`). A gestão de grupos e permissões
continua disponível pela API: `/grupos` permite consultar e criar grupos,
atribuir permissões e trocar o grupo de usuários, e `/grupos/permissoes` lista os
códigos aceitos. O último Administrador não pode ser rebaixado, para evitar
bloquear a gestão.

No `/docs`, execute `POST /autenticacao/login`, copie `access_token`, clique em
**Authorize** e cole o token Bearer. As rotas de tatuagem, imagem, agenda e grupo
passam a responder para a conta autenticada.

As permissões iniciais seguem a matriz escolhida: Cliente consulta e altera
somente as próprias tatuagens e passos; Tatuador acessa tatuagens e passos do
estúdio; Administrador tem acesso total e gerencia grupos. O cadastro público
continua criando apenas contas Cliente. A titularidade também é validada no
back, além da permissão de rota.

Exemplo de configuração pelo `/docs`:

1. Consulte `GET /grupos/permissoes` e `GET /grupos` para ver o catálogo e os
   identificadores.
2. Crie um grupo com `POST /grupos`, por exemplo:

   ```json
   {
     "codigo": "agenda",
     "nome": "Equipe da agenda",
     "permissoes": ["tatuagens:listar_todas", "tatuagens:consultar_todas"]
   }
   ```
3. Atribua uma conta ao novo grupo com `PUT /usuarios/{usuario_id}/grupo`,
   enviando `{"grupo_id": 4}` com o id devolvido pela criação.

Para trocar as permissões de um grupo existente, use
`PUT /grupos/{grupo_id}/permissoes` com a lista completa nova. Permissões não
listadas são removidas. O grupo Administrador precisa manter as permissões
necessárias para continuar gerindo o sistema.

### Se o `venv` for apagado

As dependências estão no `requirements.txt`, com as versões fixadas:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

O `fastapi-cli` é o que dá o comando `fastapi dev`: sem ele, o `fastapi.exe`
responde que falta o `fastapi[standard]` e não sobe nada. Ele já está no `venv`
deste projeto; se o comando faltar em um `venv` recriado, instale `fastapi-cli`.
O `alembic` é o que dá o comando `alembic`, para escrever e aplicar migration. O
`psycopg2-binary` é o driver do PostgreSQL, e o `pytest` roda os testes de
`backend/tests/`.

## Abrir o back

O back é o FastAPI, na pasta `backend/`. Ele sobe na porta 8000 e é ele que guarda
os dados.

```powershell
cd backend
.\venv\Scripts\activate
fastapi dev main.py --host 0.0.0.0
```

O terminal tem que mostrar que o servidor está em `0.0.0.0:8000`. Para conferir se
subiu mesmo, abra `http://127.0.0.1:8000/`; a resposta esperada é
`{"status":"ok"}`. Esse endpoint confirma a disponibilidade da API sem consultar o banco.

- `http://localhost:8000/docs` abre a documentação automática, com as rotas da API;
- o cadastro `POST /usuarios` é público e cria somente contas do grupo Cliente;
- as rotas administrativas de grupos são acessíveis somente ao grupo Administrador;
- `/autenticacao/login` aceita as credenciais de uma conta de demonstração e
  devolve o token Bearer necessário para acessar as rotas de usuários, tatuagens,
  passos, imagens, agenda e grupos;
- as imagens ficam no PostgreSQL e o download exige o mesmo token;
- a agenda é por tatuador responsável e não aceita dois horários ativos no mesmo
  bloco de uma hora.

A raiz `http://localhost:8000` responde `{"status":"ok"}` pela rota de `health`,
que confirma a disponibilidade da API sem consultar o banco. O `Caddyfile` na raiz
é do caminho local com contêineres: ele faz proxy da API na porta 80 e serve os
arquivos React que estiverem em `/srv`.

## Abrir o front

O front é o React, na pasta `frontend/`. Ele **precisa do back no ar**, porque
todas as telas chamam a API. Abra um segundo terminal para ele:

```powershell
cd frontend
npm run dev
```

O Vite abre `http://localhost:5173` e a tela de login aparece. Entre com uma das
contas de demonstração: a Bruna entra como Cliente, o Vitor como Tatuador e o
Waldemar como Administrador, e cada um vê as telas do papel dele. Esse endereço
tem que ser igual ao
`ORIGEM_FRONTEND` do `.env` da raiz, senão o navegador bloqueia a chamada por
CORS.

Para conferir o front sem depender do navegador:

- `npm run build` monta o projeto e diz se compila;
- `npm run lint` roda o oxlint e avisa se tem erro de código.

## Fechar os dois

O jeito normal é voltar ao terminal de cada servidor e apertar **Ctrl + C**. Nos
dois casos o terminal devolve o prompt e o processo morre.

Se o terminal já foi fechado, ou se você abriu os servidores de outro jeito (por
exemplo, com `Start-Process`, que abre sem janela), eles continuam rodando sem
ninguém ver. Para localizar e parar os dois de uma vez:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 5173,8000 |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

O comando pergunta ao Windows qual processo está escutando cada porta e mata esse
processo. Se não houver nada escutando, o comando não faz nada e não dá erro.

Para conferir que parou:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 5173,8000 -ErrorAction SilentlyContinue
```

Sem resultado é sinal de que os dois estão parados. Com resultado, a coluna
`OwningProcess` mostra o `ProcessId` que ainda está segurando a porta.

## O que acontece com os dados quando o back fecha

**Nada: eles continuam onde estão.** Os dados das tatuagens, das clientes, dos
passos, das imagens e da agenda estão no PostgreSQL, e fechar o back não toca em
nada disso. É a diferença entre guardar em lista na memória e guardar em banco: a
lista morre com o processo, a tabela não.

Consequência prática: o que você grava pela API continua lá depois de reiniciar o
back, e continua lá depois de trocar de máquina. Para recomeçar do zero em um
banco de estudo, apague as tabelas pelo SQL Editor do Supabase (ou por um cliente
`psql`) e rode as migrations de novo:

```powershell
cd backend
python criar_tabelas.py
```

O `criar_tabelas.py` não apaga dado nenhum: ele só aplica o que falta. Quem apaga
as tabelas é o comando de banco, e isso apaga os dados de demonstração **e** tudo
que você tenha criado pela API.

Se você quer um banco vazio sem apagar as tabelas, a ordem é a das dependências:
`DELETE FROM agendamentos; DELETE FROM tatuagem_imagens; DELETE FROM passos;
DELETE FROM tatuagens; DELETE FROM clientes;`. As contas ficam na tabela
`usuarios`, que não é apagada junto: o `DELETE FROM clientes` esvazia o
`cliente_id` das contas de cliente, e quem recria a ligação é o
`criar_contas_de_demonstracao.py`.

## Mudança no banco depois que ele já existe

Não se mexe no banco com `ALTER TABLE` escrito à mão. O desenho mora nos modelos,
em `backend/modelos/`, e a mudança vira uma migration, que é um arquivo `.py` no
Git. Do terminal de `backend/`, com o venv ativo:

```powershell
alembic revision --autogenerate -m "o que mudou"   # escreve a migration
alembic upgrade head                              # aplica no banco
```

Sempre na mesma ordem, e **lendo o arquivo gerado antes de aplicar**. O README
explica o porquê de cada comando.

## Resumo em uma tela

| | abrir | conferir | fechar |
| --- | --- | --- | --- |
| back | `cd backend` · `.\venv\Scripts\activate` · `fastapi dev main.py` | `http://localhost:8000/docs` | `Ctrl + C`, ou o comando de porta |
| front | `cd frontend` · `npm run dev` | `http://localhost:5173` | `Ctrl + C`, ou o comando de porta |

Os dois precisam estar abertos ao mesmo tempo para o site funcionar: o front sem o
back mostra o aviso de erro, porque não tem quem responda.
