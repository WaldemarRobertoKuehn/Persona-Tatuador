# Como rodar e como fechar

Este arquivo é o passo a passo do dia a dia: o que fazer para abrir o projeto e o que
fazer para fechar. Os dois servidores são processos que ficam rodando até serem
parados, e é por isso que o site continua respondendo no navegador depois de você
fechar a aba.

## O que precisa existir na máquina

- **MySQL**, para o banco. Precisa estar no ar e o banco `traco_fino` precisa existir.
- **Python**, para o back. O `venv` já está criado em `backend/venv`, então não é
  preciso instalar nada: é só ativar.
- **Node.js**, para o front. O `node_modules` já está em `frontend/`, então
  `npm install` só é preciso se você apagar essa pasta.

### Se o banco não existir ainda

O back não sobe sem o MySQL, porque é nele que os dados moram. O desenho do banco
está em `backend/esquema.sql`, que cria as três tabelas e já entra com os dados de
demonstração:

```powershell
cd backend
mysql -u root -p < esquema.sql
```

A senha é pedida pelo próprio `mysql`, não vai no comando.

### Se o `venv` for apagado

São sete pacotes, e o README explica o porquê de cada um:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install fastapi fastapi-cli "uvicorn[standard]" sqlalchemy pymysql python-dotenv alembic
```

O `fastapi-cli` é o que dá o comando `fastapi dev`: sem ele, o `fastapi.exe`
responde que falta o `fastapi[standard]` e não sobe nada. O `alembic` é o que dá o
comando `alembic`, para escrever e aplicar migration.

## Abrir o back

O back é o FastAPI, na pasta `backend/`. Ele sobe na porta 8000 e é ele que guarda
os dados.

```powershell
cd backend
.\venv\Scripts\activate
fastapi dev main.py
```

O terminal tem que mostrar algo como `http://localhost:8000`. Para conferir se
subiu mesmo:

- `http://localhost:8000/docs` abre a documentação automática, com as cinco rotas
  da cartilha;
- `http://localhost:8000/tatuagens` responde com as **oito tatuagens de
  demonstração**.

A raiz `http://localhost:8000` responde **404**, e isso é de propósito: a REGRAS
proíbe rota no `main.py`.

## Abrir o front

O front é o React, na pasta `frontend/`. Ele **precisa do back no ar**, porque
todas as telas chamam a API. Abra um segundo terminal para ele:

```powershell
cd frontend
npm run dev
```

O Vite abre `http://localhost:5173` e a tela de escolha de perfil aparece, com a
Bruna e o Vitor. Esse endereço tem que ser igual ao `ORIGEM_FRONTEND` do
`backend/.env`, senão o navegador bloqueia a chamada por CORS.

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

**Nada: eles continuam onde estão.** Os dados das tatuagens, das clientes e dos
passos estão no MySQL, e fechar o back não toca em nada disso. É a diferença entre
guardar em lista na memória e guardar em banco: a lista morre com o processo, a
tabela não.

Consequência prática: o que você grava pela API continua lá depois de reiniciar o
back, e continua lá depois de trocar de máquina. Para desfazer, apaga o banco e
roda o `esquema.sql` de novo:

```powershell
mysql -u root -p -e "DROP DATABASE traco_fino"
cd backend
mysql -u root -p < esquema.sql
```

Isso apaga os dados de demonstração **e** tudo que você tenha criado pela API, e
só é seguro porque é um banco de estudo.

Se você quer a API vazia, sem apagar nada: `DELETE FROM passos; DELETE FROM
tatuagens; DELETE FROM clientes;`, nessa ordem, porque o passo aponta para a
tatuagem e a tatuagem aponta para a cliente.

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
