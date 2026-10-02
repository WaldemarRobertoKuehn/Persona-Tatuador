# Front do Traço Fino

O React do estúdio de tatuagem, em `src/`. São quatro telas, e cada uma é um componente em
`src/telas/`. Quem decide qual tela aparece é o `src/App.jsx`, e ele só tem dois estados: o perfil
escolhido e a tela atual.

## Como rodar

O front precisa do back no ar, porque todas as telas chamam a API.

```bash
cd frontend
npm install
npm run dev
```

O Vite abre `http://localhost:5173`. Esse endereço tem que ser igual ao `ORIGEM_FRONTEND` do `.env`
do back, porque é dele que sai o CORS. Se o Vite subir em outra porta, o navegador bloqueia a
chamada e a tela fica mostrando o aviso de erro.

| comando | o que faz |
| --- | --- |
| `npm run dev` | sobe o servidor de desenvolvimento, com recarga automática |
| `npm run build` | gera a versão de produção em `dist/` |
| `npm run preview` | serve o `dist/` para conferir como fica a versão de produção |
| `npm run lint` | passa o oxlint, que é o que avisa de código esquecido |

## O que tem em `src/`

| arquivo | o que é |
| --- | --- |
| `main.jsx` | o ponto de entrada, e a ordem em que o CSS entra |
| `App.jsx` | o perfil escolhido e a tela atual |
| `perfis.js` | a lista fixa de perfis e a ordem das telas de cada um |
| `api.js` | o único arquivo que sabe a porta do back e o único que usa `fetch` |
| `componentes/Etiqueta.jsx` | a etiqueta colorida da etapa |
| `componentes/Avisos.jsx` | os avisos de carregando, de erro e de lista vazia |
| `telas/` | as telas |
| `estilos/tokens.css` | as variáveis de cor, espaço e fonte do styleguide |
| `estilos/base.css` | o que toda tela tem, e os componentes que se repetem |

## As telas

| tela | quem usa | aparelho | arquivo |
| --- | --- | --- | --- |
| Pedir tatuagem | Bruna | celular | `telas/PedirTatuagem.jsx` |
| Minhas tatuagens | Bruna | celular | `telas/MinhasTatuagens.jsx` |
| A agenda | Vitor | computador | `telas/Agenda.jsx` |
| A ficha | Vitor | computador | `telas/Ficha.jsx` |

A escolha de perfil, `telas/EscolhaPerfil.jsx`, não é uma das quatro telas da cartilha, mas a
cartilha pede: enquanto o login não chega, o front deixa escolher o perfil numa lista, sem senha.

**As telas do Vitor são as do computador, e isso muda o desenho.** O filtro da agenda são abas na
horizontal e a lista é uma tabela com a coluna da cliente. No celular a mesma tabela vira uma lista
de cartões, e cada cartão repete o nome da coluna. Quem faz essa troca é o CSS, e não o
JavaScript: a tabela é uma só no documento, e o que muda é a apresentação.

**A ficha não esconde os passos que a regra recusa.** O seletor traz os três tipos sempre, mesmo
os que a etapa atual não aceita. Se a tela escondesse, o Vitor nunca veria a recusa, e a recusa é
parte do que ele precisa entender. Depois de registrar, a ficha relê a tatuagem e o histórico,
porque a resposta do registro é o passo, e a etapa é outro recurso da API.

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
