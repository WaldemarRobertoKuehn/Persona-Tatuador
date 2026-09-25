# Marca · Traço Fino

A identidade do Traço Fino, que é escolha minha. A cartilha avisa que dois alunos
receberam o mesmo problema e que **não se pode combinar marca** com o colega de
cartilha. O nome do estúdio, a cor, a tipografia e o desenho do logo são meus.

A paleta e a tipografia que a marca usa estão detalhadas em
[`styleguide/styleguide.md`](styleguide/styleguide.md). Este documento
fala do que é a marca; o styleguide fala de como as telas usam ela.

Os quatro arquivos da marca estão na pasta `marca/`, ao lado deste documento, e
são eles que a interface usa.

## 1. A ideia da marca

O estúdio faz tatuagem de **traço fino**: linha delicate, contorno, muito preto
e pouca mancha. A marca precisa contar isso sem desenhar uma agulha.

Por isso a marca é uma **palavra e uma linha**. "Traço Fino" escrito numa
tipografia de contraste alto, e uma linha fina de 1,5 px atravessando embaixo,
que é literalmente o traço do estúdio. Não há agulha, não há mão, não há
tribo. Quem vê a marca e depois entra na agenda entende a mesma coisa.

A linha também é a assinatura: é a única parte colorida do logo, e por isso ela é
o acento `#C2410C`. Um único detalhe de cor em um desenho quase todo preto é
mais forte do que um logo inteiro colorido.

## 2. As versões

| arquivo | versão | fundo | quando usar |
| --- | --- | --- | --- |
| `logo.svg` | principal | claro | padrão, tudo que é tela |
| `logo-escuro.svg` | invertida | escuro | rodapé escuro, capa de sessão |
| `logo-monocromatico.svg` | monocromática | claro ou escuro | carimbo, bordado, crachá, impressão em uma cor |
| `simbolo.svg` | símbolo | claro | favicon, quadrinho do app, marca d'água |

O símbolo é a letra T e a letra F com a linha embaixo. Em 32 pixels a palavra
inteira vira borra, então em lugar pequeno vai o símbolo, e só ele.

A regra "não trocar as cores" tem uma consequência prática: como o sistema tem
tema escuro, a interface **troca de arquivo** quando o tema muda, em vez de
repintar o logo. No tema claro ela pede `logo.svg`, no escuro pede
`logo-escuro.svg`, e a pessoa não vê a troca acontecer. Um logo que mudasse de cor
por CSS seria uma quarta versão que ninguém desenhou.

### A letra está desenhada em curva

Os quatro arquivos têm a palavra (e as letras do símbolo) como `<path>`, e não
como texto. Isso não é preciosismo de designer: um SVG aberto com `<img>` é um
documento separado, e ele não enxerga a fonte que a página carregou. Com a letra
escrita como texto, o logo apareceria na Georgia em toda máquina que não tivesse
a Playfair Display instalada, e a aba do navegador — que é o símbolo — ficaria
diferente em cada computador. Em curva, o logo é o mesmo com ou sem a fonte, e é
também o que permite imprimir sem worry sobre fonte instalada.

O `@font-face` do site continua carregando a Playfair Display para os **títulos**,
que é onde a fonte aparece como texto. Nenhuma parte da letra do logo foi
modificada, e a licença original da fonte continua valendo. A letra em curva
também é o que permite imprimir o logo sem se preocupar com fonte instalada.

## 3. O que a marca diz sobre o sistema

Não é enfeite: cada escolha resolve um problema do produto.

- **Uma linha, não uma agulha.** O estúdio valoriza linha fina, não máquina. A
  agulha seria um ícone genérico de app de clínica.
- **Preto com um acento, em tudo.** É a mesma regra do styleguide: uma cor de
  destaque, no máximo um elemento por tela. A marca segue a própria regra.
- **Serifada de contraste alto nos títulos.** A letra do logo já tem traço grosso
  e traço fino. O nome se explica desenhado.
- **Sem slogan.** Quem chega ao sistema já sabe o que é estúdio de tatuagem, e
  slogan ocupa o espaço onde a etapa da tatuagem precisa aparecer.

## 4. Regras de uso

- **Espaço de respiro:** ao redor do logo, um espaço livre do tamanho da altura da
  letra. Nada encostando.
- **Tamanho mínimo:** abaixo de 120 px de largura, usar `simbolo.svg`.
- **A linha tem 1,5 px** e essa espessura não muda. Se a linha engrossar, a
  marca perde a única coisa que ela afirma.
- **A linha sublinha a palavra, e não a caixa.** Ela começa na primeira letra e
  termina na última. A caixa do arquivo mede 250×71 para acompanhar a palavra, e
  a palavra de 46 ocupa 233 px, com os 8 px de recuo de cada lado. Uma linha que
  fosse de ponta a ponta da caixa deixaria 98 px de traço solto depois do desenho,
  e traço solto não é sublinhado: é ruído.
- **Não esticar e não rotacionar.** Os SVG têm largura e altura, e é para isso que
  servem. Quem mostra o logo em tela tem que respeitar a proporção 250 por 71; no
  `Logo.jsx` esses dois números estão em `width` e `height` juntos, e é isso que
  impede o navegador de achatar o desenho.
- **Não trocar as cores** do logo para caber em um fundo. Se o fundo não é claro
  nem escuro o bastante, o problema é o fundo.
- **Não pôr o logo sobre foto de tatuagem.** Foto do trabalho não usa marca em
  cima: o trabalho é o conteúdo.

## 5. O que ainda não existe

Isto aqui é a marca para o sistema, e foi desenhado em SVG de propósito, para o
arquivo ser do repositório e versionar junto com o código.

O que já foi resolvido: o **logo em alta**, com a letra convertida em curva, para
não depender de fonte instalada. Está pronto nos quatro arquivos, e é o que a
seção acima explica. O que converter ainda falta, se um dia for preciso, é a
**expansão em alta resolução** para gráfica profissional, que é outro problema: o
de largura de traço em 300 dpi, não o de fonte.

Fica pendente, e continua sendo decisão minha:

- o **manual em PDF**, se a entrega exigir;
- o **Figma** da marca, caso eu queira passar a desenhar nele em vez de escrever
  SVG à mão.
