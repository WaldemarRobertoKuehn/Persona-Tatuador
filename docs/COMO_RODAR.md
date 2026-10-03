# Como rodar e como fechar

Este arquivo é o passo a passo do dia a dia: o que fazer para abrir o projeto e o que
fazer para fechar. Os dois servidores são processos que ficam rodando até serem
parados, e é por isso que o site continua respondendo no navegador depois de você
fechar a aba.

## O que precisa existir na máquina

- **Python**, para o back. O `venv` já está criado em `backend/venv`, então não é
  preciso instalar nada: é só ativar.
- **Node.js**, para o front. O `node_modules` já está em `frontend/`, então
  `npm install` só é preciso se você apagar essa pasta.

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

A lista de tatuagens fica **na memória do processo**, dentro dos arquivos de
`repositorios/`. Ela não está em disco: quando o uvicorn para, a lista morre com
ele, e na volta seguinte o back abre com as oito tatuagens de demonstração de
novo. Isso é o que a REGRAS pede, e é o motivo de não existir banco de dados no
projeto.

Se você quiser a API vazia para testar o pedido de tatuagem do zero, apague o
bloco `..._de_exemplo` no fim de cada arquivo de `repositorios/`.

## Resumo em uma tela

| | abrir | conferir | fechar |
| --- | --- | --- | --- |
| back | `cd backend` · `.\venv\Scripts\activate` · `fastapi dev main.py` | `http://localhost:8000/docs` | `Ctrl + C`, ou o comando de porta |
| front | `cd frontend` · `npm run dev` | `http://localhost:5173` | `Ctrl + C`, ou o comando de porta |

Os dois precisam estar abertos ao mesmo tempo para o site funcionar: o front sem o
back mostra o aviso de erro, porque não tem quem responda.