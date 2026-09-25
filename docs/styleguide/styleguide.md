# Styleguide · Traço Fino

Este documento é a referência de estilo do sistema. A paleta e a tipografia aqui
definidas são escolha minha, e a cartilha avisa que não se pode combinar paleta
com o colega de cartilha.

O styleguide não é enfeite: é o contrato entre as quatro telas. Se uma tela
usar uma cor ou uma fonte que não está aqui, ela está errada.

## 1. Cores

A base é preto e branco, com **uma** cor de destaque. A regra de ouro: o acento
aparece no máximo em um elemento por tela. Quando tudo é destaque, nada é.

| token | valor | onde entra |
| --- | --- | --- |
| `--cor-texto` | `#111111` | títulos e texto do corpo |
| `--cor-texto-fraco` | `#52525B` | legenda, rótulo de campo, data |
| `--cor-fundo` | `#FFFFFF` | fundo das telas |
| `--cor-superficie` | `#F4F4F5` | cartão, campo de formulário, linha da tabela |
| `--cor-borda` | `#E4E4E7` | borda de cartão e de campo |
| `--cor-acento` | `#C2410C` | botão principal e a etiqueta da etapa que precisa de ação |

### Contraste

Estes números saíram de cálculo, não de palpite. A regra é a WCAG 2.1: **4,5:1**
para texto normal e **3:1** para texto grande.

| combinação | contraste | veredito |
| --- | --- | --- |
| `#111111` sobre `#FFFFFF` | **18,88:1** | passa em AA e AAA |
| `#111111` sobre `#F4F4F5` | **17,18:1** | passa em AA e AAA |
| `#52525B` sobre `#F4F4F5` | **7,03:1** | passa em AA e AAA |
| `#FFFFFF` sobre `#C2410C` (botão) | **5,18:1** | passa em AA |

A borda `#E4E4E7` sobre branco dá 1,27:1, e isso é intencional: borda de cartão é
decoração, não informação. Se algum dia uma borda carregar sentido, ela tem de
escurecer para passar em 3:1.

### A cor de cada etapa

A etapa é a informação mais importante da tela, e são quatro. Com uma cor só de
destaque, a solução é não dar destaque às quatro: o acento fica com a etapa em
que o estúdio precisa agir.

| etapa | fundo | texto | por quê |
| --- | --- | --- | --- |
| `pedida` | `#F4F4F5` | `#111111` | neutra: ainda nem chegou no tatuador |
| `desenho aprovado` | `#E4E4E7` | `#111111` | neutra: o próximo passo é uma sessão |
| `em sessões` | `#C2410C` | `#FFFFFF` | **o destaque**: é aqui que o Vitor trabalha |
| `finalizada` | `#111111` | `#FFFFFF` | fechada, e o preto diz "pronto" |

Como ler essa tabela: fundo claro é "está esperando", fundo escuro é "acabou", e
o laranja é "é agora". Uma tela com três etiquetas de etapa mostra isso sem
precisar de legenda.

## 2. Tipografia

Duas fontes, com um trabalho para cada uma.

**Corpo, rótulos, botões e dados: a sans-serif do sistema.** A pilha é

```
system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
```

O motivo é prático e defensável: não precisa baixar nada, já está no Windows, no
Mac e no celular, e nunca aparece um texto quebrado na apresentação. Fonte de
corpo não é lugar de arriscar.

**Logo e títulos: Playfair Display**, com queda para `Georgia, serif`. O nome da
fonte não é o argumento. O argumento é que essa serifada tem contraste alto,
isto é, traço grosso e traço fino na mesma letra. O nome do estúdio é *Traço
Fino*, e a própria letra do logo é uma demonstração do nome. Se a fonte não
carregar na apresentação, a queda para Georgia mantém a ideia.

| uso | tamanho | peso | entrelinha |
| --- | --- | --- | --- |
| Título de tela | 1,5 rem | 600 | 1,3 |
| Título de seção | 1,125 rem | 600 | 1,4 |
| Corpo | 1 rem | 400 | 1,5 |
| Rótulo e legenda | 0,8125 rem | 500 | 1,4 |

O corpo nunca sai de 1 rem. As quatro telas são lidas no celular, e texto miúdo é
o primeiro defeito de interface que aparece quando a tela é pequena.

## 3. Espaço, raio e sombra

| token | valor | uso |
| --- | --- | --- |
| `--espaco-1` | 0,25 rem | aperto interno |
| `--espaco-2` | 0,5 rem | entre etiqueta e texto |
| `--espaco-3` | 1 rem | entre campos |
| `--espaco-4` | 1,5 rem | dentro do cartão |
| `--espaco-5` | 3 rem | entre cartões |
| `--raio` | 0,5 rem | botão, campo, cartão |
| `--sombra` | `0 1px 2px rgba(0,0,0,.08)` | só no cartão flutuante |

Tudo em `rem`, para o navegador aplicar o tamanho que a pessoa escolheu nas
acessibilidade. Sombra só quando o cartão realmente flutua; sombra em tudo vira
sujeira.

## 4. Componentes

**Botão principal.** Fundo `#C2410C`, texto `#FFFFFF`, raio `--raio`, altura
mínima de 2,75 rem. Altura mínima porque é alvo de dedo: 44 px é o piso.

**Campo de formulário.** Rótulo em `--cor-texto-fraco` e 0,8125 rem, campo com
fundo `--cor-superficie` e borda `--cor-borda`. O erro aparece **embaixo** do
campo, na cor do acento, com o texto do motivo, e não só uma borda vermelha.

**Cartão de tatuagem.** Fundo branco, borda de 1 px, raio `--raio`. Mostra, nesta
ordem: a etapa (etiqueta), a ideia, o local e o tamanho, e o nome da cliente. A
etiqueta fica em cima à direita, porque a etapa é o que se procura primeiro.

**Etiqueta de etapa.** Cantos arredondados, texto de 0,8125 rem em maiúscula, e
a cor vem da tabela da seção 1. Sem borda: a cor do fundo já separa.

## 5. As duas telas não são a mesma tela encolhida

A cartilha é clara: o aparelho de cada perfil diz onde a tela precisa estar
impecável. Isso vira regra de código.

1. **Escrevo para o celular primeiro.** O CSS é mobile-first, e a regra de
  (width) maior entra por `@media (min-width: 48rem)`. Nenhuma tela ganha
   ajuste para o computador antes de funcionar no celular.
2. **Telas 1 e 2 (Bruna) são pensadas para o celular.** Uma coluna, botão
   fixo embaixo, tabela vira lista de cartões.
3. **Telas 3 e 4 (Vitor) são pensadas para o computador.** Filtro de etapa em
   abas na horizontal, lista em tabela com a coluna da cliente visível, e a ficha
   com o formulário em duas colunas para não esticar o campo no meio da tela.
4. **As quatro funcionam nos dois tamanhos.** Quem abre a agenda no celular
   recebe a mesma informação, empilhada. Isso não muda o que a tela diz, muda
   como ela se acomoda.
5. **A lista de tattooagens nunca fica dentro de um contêiner com largura fixa.**
   A largura máxima é só para o texto, senão a linha some em tela grande.

## 6. O que não entra

- **Gradiente.** Um só acento, chapado.
- **Sombra em texto.** Nenhuma.
- **Animação de entrada.** Só a troca de estado de carregamento, e ela precisa
  respeitar quem desativou animação no sistema.
- **Cor fora da paleta.** Se a tela precisa de uma cor nova, o problema é a
  hierarquia de informação, não a paleta.
- **Ícone no lugar de palavra.** Botão de registro de passo é "Registrar passo",
  não um desenho de agulha.
