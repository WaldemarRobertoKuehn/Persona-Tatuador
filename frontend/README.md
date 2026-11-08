# Front do Traço Fino

O React do estúdio de tatuagem, em `src/`. São **sete telas** em `src/telas/`: as quatro da cartilha
(Pedir tatuagem, Minhas tatuagens, A agenda e A ficha) e três de apoio (Login, Administração e
Alterar senha). Quem decide qual tela aparece é o `src/App.jsx`: a conta autenticada, a tela atual e
a tatuagem aberta.

## Como rodar

O front precisa do back no ar, porque todas as telas chamam a API.

```bash
cd frontend
npm install
npm run dev
```

O Vite abre `http://localhost:5173`. Esse endereço tem que ser igual ao `ORIGEM_FRONTEND` do `.env`
da raiz do repositório, porque é dele que sai o CORS. Se o Vite subir em outra porta, o navegador
bloqueia a chamada e a tela fica mostrando o aviso de erro.

| comando | o que faz |
| --- | --- |
| `npm run dev` | sobe o servidor de desenvolvimento, com recarga automática |
| `npm run build` | gera a versão de produção em `dist/` |
| `npm run preview` | serve o `dist/` para conferir como fica a versão de produção |
| `npm run lint` | passa o oxlint, que é o que avisa de código esquecido |

O endereço da API vem de `VITE_URL_DA_API`, lido em `src/api.js`:

| arquivo | valor | uso |
| --- | --- | --- |
| `.env.development` | `http://localhost:8000` | desenvolvimento local |
| `.env.production` | `/api` | produção, na mesma origem da tela ou atrás do proxy da Vercel |

## O que tem em `src/`

| arquivo | o que é |
| --- | --- |
| `main.jsx` | o ponto de entrada, e a ordem em que o CSS entra |
| `App.jsx` | a conta autenticada, a tela atual e a tatuagem aberta |
| `perfis.js` | os perfis, a ordem das telas de cada papel e as etapas da cartilha |
| `api.js` | o único lugar do front que usa `fetch`, com token e tratamento de erros |
| `datas.js` | ISO do back virando `dd/mm/aaaa` e hora na tela |
| `tema.js` | o tema claro/escuro e a persistência no navegador |
| `componentes/` | as peças repetidas: logo, tema, senha, avisos, imagens, agenda e linha do tempo |
| `telas/` | as telas |
| `estilos/tokens.css` | as variáveis de cor, espaço e fonte do styleguide |
| `estilos/base.css` | o que toda tela tem, e os componentes que se repetem |
| `fontes/` | a Playfair Display, com a licença e a procedência |
| `imagens/` | as fotos do ateliê e da vitrine, importadas pelo build |

## Autenticação e perfis

`telas/Login.jsx` envia e-mail e senha em `POST /autenticacao/login`. A resposta traz o token e os
dados públicos da conta; o token fica na sessão da aba (`sessionStorage`, chave
`traco-fino-token`). Ao reabrir ou atualizar a página, o front valida o token em
`GET /usuarios/eu`; quando o prazo gravado no próprio JWT vence, limpa a sessão e pede novo login.

O perfil vem do **papel** devolvido pelo back (`cliente`, `tatuador` ou `administrador`). O front
não tem id de usuário escrito no código, e as permissões do grupo vêm no login e em `/usuarios/eu`.
Quem decide o que cada botão faz é o back; a tela usa as permissões só para esconder ações que
seriam recusadas.

A mesma tela alterna para:

- **cadastro**, que envia nome, e-mail e senha em `POST /usuarios`; o back cria sempre uma conta
  Cliente e não inicia sessão;
- **esqueci minha senha**, que chama `POST /autenticacao/esqueci-senha` e envia um link por SMTP;
- **redefinir senha**, aberta quando a URL chega com o token no hash (`#redefinir-senha=...`), que
  chama `POST /autenticacao/redefinir-senha`.

A tela **Alterar senha** chama `POST /autenticacao/alterar-senha`, confere a senha atual e pede a
nova duas vezes.

## As telas

| tela | quem usa | aparelho | arquivo |
| --- | --- | --- | --- |
| Login, cadastro e recuperação | todos | ambos | `telas/Login.jsx` |
| Pedir tatuagem | Cliente | celular | `telas/PedirTatuagem.jsx` |
| Minhas tatuagens | Cliente | celular | `telas/MinhasTatuagens.jsx` |
| A agenda | Tatuador | computador | `telas/Agenda.jsx` |
| A ficha | Tatuador | computador | `telas/Ficha.jsx` |
| Administração | Administrador | computador | `telas/Administracao.jsx` |
| Alterar senha | todos | ambos | `telas/AlterarSenha.jsx` |

A tela da cliente usa o `cliente_id` que vem na conta, e não o id da conta: a conta e a cliente da
cartilha são duas coisas diferentes, e quem guarda a ligação entre elas é o back.

**As telas do tatuador são as do computador, e isso muda o desenho.** O filtro da agenda são abas na
horizontal e a lista é uma tabela com a coluna da cliente. No celular a mesma tabela vira uma lista
de cartões, e cada cartão repete o nome da coluna. Quem faz essa troca é o CSS, e não o JavaScript:
a tabela é uma só no documento, e o que muda é a apresentação.

**A ficha não esconde os passos que a regra recusa.** O seletor traz os três tipos sempre, mesmo os
que a etapa atual não aceita. Se a tela escondesse, o tatuador nunca veria a recusa, e a recusa é
parte do que ele precisa entender. Depois de registrar, a ficha relê a tatuagem e o histórico,
porque a resposta do registro é o passo, e a etapa é outro recurso da API.

**A administração cadastra a equipe.** A tela lista os tatuadores (`GET /usuarios/tatuadores`), cria
novas contas de tatuador (`POST /usuarios/tatuadores`) e atribui o responsável de uma tatuagem
(`PUT /tatuagens/{id}/tatuador`). A gestão de grupos e permissões continua disponível pela API, em
`/grupos` e `/usuarios/{id}/grupo`.

## As imagens e a agenda na tela

O componente `ImagensDaTatuagem` é usado pela ficha e pela tela da cliente. O cliente envia
referência e aprova ou recusa o desenho; o tatuador envia o desenho e pode removê-lo. O arquivo é
lido por `fetch` autenticado e vira um object URL, porque um `<img src="/...">` não envia o
cabeçalho `Authorization`. O limite de 4 MB e os tipos JPEG, PNG e WebP são repetidos na tela só
para avisar antes do upload; a recusa de verdade é do back.

O componente `AgendaDaTatuagem` mostra as sessões e o retoque. A disponibilidade vem pronta do back
(`GET .../agendamentos/disponibilidade?data=...`), porque o expediente e os horários ocupados são
regra do servidor. O tatuador responsável marca e cancela; outro tatuador pode consultar, mas não
gerenciar a agenda alheia. Cada horário ocupa uma hora.

## Componentes

| componente | o que faz |
| --- | --- |
| `Logo.jsx` | mostra `/logo.svg` ou `/logo-escuro.svg`, servidos de `docs/marca/` |
| `AlternadorTema.jsx` | alterna claro/escuro e reflete o estado em `aria-pressed` |
| `CampoSenha.jsx` | campo de senha com botão de mostrar/ocultar |
| `CabecalhoDaTela.jsx` | título, linha de apoio e ação principal de uma tela |
| `Avisos.jsx` | os estados de carregando, erro e lista vazia |
| `Etiqueta.jsx` | a etiqueta colorida da etapa |
| `ProgressoDasEtapas.jsx` | a régua das quatro etapas da cartilha |
| `LinhaDoTempo.jsx` | a lista de passos com tipo, data e observação |
| `ImagensDaTatuagem.jsx` | upload, listagem, aprovação, recusa e remoção de imagens |
| `MiniaturaDoDesenho.jsx` | a miniatura do desenho na lista da agenda |
| `AgendaDaTatuagem.jsx` | sessões, retoque, disponibilidade e cancelamento |

## Funções de `api.js`

| grupo | funções |
| --- | --- |
| sessão | `autenticar`, `buscarUsuarioAtual`, `tokenSalvo`, `guardarToken`, `limparToken`, `milissegundosAteExpirar` |
| senha | `solicitarRedefinicaoSenha`, `redefinirSenha`, `alterarSenha` |
| contas | `cadastrarUsuario`, `buscarTatuadores`, `cadastrarTatuador` |
| tatuagens | `buscarTatuagens`, `buscarTatuagem`, `criarTatuagem`, `atribuirTatuador` |
| passos | `buscarPassos`, `registrarPasso` |
| imagens | `buscarImagens`, `enviarImagem`, `buscarConteudoImagem`, `aprovarImagem`, `recusarImagem`, `removerImagem` |
| agenda | `buscarAgendamentos`, `buscarDisponibilidade`, `criarAgendamento`, `cancelarAgendamento` |

## Três coisas que valem saber antes de mexer

**A cor está em um lugar só.** Nenhuma tela escreve um código de cor. Se um componente precisa de
cor, ele usa uma variável de `estilos/tokens.css`. É o que mantém a regra do styleguide valendo no
código, e não só no desenho.

**Toda tela que chama o back tem três estados.** Começa carregando, passa a estar pronta quando a
chamada volta, e vira erro se a chamada falhar. Quem cuida disso é o `useState` de cada tela, e os
dois avisos são o `componentes/Avisos.jsx`. Nenhuma tela chama `fetch` direto: quem chama é o
`api.js`, para o tratamento de erro ficar escrito uma vez só.

**O CSS é mobile-first.** O que está fora do `@media` vale para o celular, e a regra com
`--tela-grande` é o ajuste para a tela de computador. Nenhuma tela ganha ajuste de computador antes
de funcionar no celular.
