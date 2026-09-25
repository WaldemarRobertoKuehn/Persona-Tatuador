# Marca · Traço Fino

A identidade do Traço Fino, que é escolha minha. A cartilha avisa que dois alunos
receberam o mesmo problema e que **não se pode combinar marca** com o colega de
cartilha. O nome do estúdio, a cor, a tipografia e o desenho do logo são meus.

A paleta e a tipografia que a marca usa estão detalhadas em
[`../styleguide/styleguide.md`](../styleguide/styleguide.md). Este documento
fala do que é a marca; o styleguide fala de como as telas usam ela.

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
- **Não esticar e não rotacionar.** Os SVG têm largura e altura, e é para isso que
  servem.
- **Não trocar as cores** do logo para caber em um fundo. Se o fundo não é claro
  nem escuro o bastante, o problema é o fundo.
- **Não pôr o logo sobre foto de tatuagem.** Foto do trabalho não usa marca em
  cima: o trabalho é o conteúdo.

## 5. O que ainda não existe

Isto aqui é a marca para o sistema, e foi desenhado em SVG de propósito, para o
arquivo ser do repositório e versionar junto com o código. Fica pendente, e
continua sendo decisão minha:

- o **logo em alta**, para impressão, com as fontes e o traço convertidos em
  curvas, para não depender de fonte instalada;
- o **manual em PDF**, se a entrega exigir;
- o **Figma** da marca, caso eu queira passar a desenhar nele em vez de escrever
  SVG à mão.
