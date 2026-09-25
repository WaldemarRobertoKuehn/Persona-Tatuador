# Briefing · Traço Fino, estúdio de tatuagem

Este documento diz **o que o sistema precisa fazer**. A fonte de verdade é `docs/CARTILHA.md`, que
não foi alterada. Aqui eu explico a intenção por trás dela, que é o que eu defendo na apresentação.

## 1. O negócio

O **Traço Fino** é um estúdio de tatuagem pequeno, com dois tatuadores. O dono é o **Vitor**, que
também tatua, e é ele quem organiza a agenda do estúdio. O trabalho nunca acaba no balcão: toda
tatuagem passa por etapas, o desenho precisa ser aprovado, vem uma ou mais sessões, e quando a pele
cicatriza vem o retoque. Entre uma etapa e outra existem dias de espera, e o que o estúdio precisa é
de uma agenda que separe o que já foi feito do que ainda vai ser.

O nome veio da própria cartilha. A cartilha avisa que dois alunos receberam o mesmo problema e que
não se pode combinar marca, paleta, telas nem nomes de rota entre os dois. Tudo que aparece aqui é
escolha minha.

## 2. O problema

Hoje esse acompanhamento vive em conversa de mensagem. Isso custa caro em três coisas concretas:

1. **Ninguém sabe em que etapa está cada cliente.** O cliente pergunta "já tá pronto?", e o
   tatuador precisa garimpar mensagens para responder.
2. **O histórico se perde.** O que foi feito na primeira sessão, em que dia o desenho foi
   aprovado, se o retoque já aconteceu: fica na memória de quem tatua.
3. **A agenda fica no caos.** Entre uma sessão e outra não existe lugar nenhum que mostre quais
   tatuagens estão esperando o próximo passo.

Em uma frase: **cada tatuagem é um compromisso com data, e o estúdio não tem onde anotar o que já
foi feito.**

## 3. Quem usa

### Bruna, a cliente. Usa no celular.

Tem 27 anos, é designer, e vai fazer a primeira tatuagem grande. Ela não conhece o vocabulário do
estúdio, então precisa descrever a ideia do jeito dela, e precisa saber sempre o que vem depois.

O que ela faz no sistema:

1. **Pede uma tatuagem**, dizendo a ideia, o local do corpo e o tamanho.
2. **Vê as tatuagens dela**, com a etapa de cada uma.
3. **Abre uma tatuagem** e lê o histórico: desenho, sessões e retoque.

O que ela não é: cliente de loja, não negocia preço, não envia foto. Ela quer saber a etapa.

### Vitor, o tatuador. Usa no computador.

Vitor tatua e organiza a própria agenda. Entre uma sessão e outra ele precisa registrar o que foi
feito, sem perder tempo, e ver de relance o que está parado esperando ele.

O que ele faz no sistema:

1. **Vê as tatuagens, filtradas por etapa.** A agenda é a tela que ele abre primeiro.
2. **Abre uma tatuagem e registra um passo**: o desenho aprovado, uma sessão ou o retoque.
3. **Confere que a etapa mudou.** O registro precisa dar retorno visível, senão ele não sabe se
   funcionou.

## 4. A regra que o serviço cuida

Esta é a única regra de negócio do sistema inteiro, e ela é o coração do trabalho.

A tatuagem nova nasce como **pedida**. Os passos seguem uma ordem obrigatória:

```
pedida              --(desenho aprovado)-->  desenho aprovado
desenho aprovado    --(sessão)----------->  em sessões
em sessões          --(sessão)----------->  em sessões
em sessões          --(retoque)---------->  finalizada
```

Duas recusas vêm dessa ordem:

- **Sessão antes do desenho aprovado é recusada.** Não se tatua o que não foi aprovado.
- **Retoque antes de pelo menos uma sessão é recusado.** Retoque só existe depois da cicatrização,
  e cicatrização só existe depois que houve tatuagem.

| etapa em que a tatuagem está | passo aceito | para onde vai |
| --- | --- | --- |
| pedida | desenho aprovado | desenho aprovado |
| desenho aprovado | sessão | em sessões |
| em sessões | sessão | em sessões |
| em sessões | retoque | finalizada |

Repare que **sessão pode se repetir** e que o passo aceito é o que muda a etapa, nunca o contrário.
E é por isso que a tela do Vitor precisa mostrar a etapa depois do registro: é o único jeito dele
saber que a regra rodou.

## 5. As quatro telas

| tela | de quem | onde tem que estar impecável | o que resolve |
| --- | --- | --- | --- |
| **1. Pedir tatuagem** | Bruna | celular | ela descreve a ideia e o corpo, sem jargão |
| **2. Minhas tatuagens** | Bruna | celular | ela vê a etapa de cada uma e abre o histórico |
| **3. A agenda** | Vitor | computador | ele filtra por etapa e vê o que está esperando |
| **4. A ficha** | Vitor | computador | ele registra o passo e confirma a etapa nova |

Duas regras de layout que eu carrego para o código:

1. **Todas as quatro telas funcionam nos dois tamanhos.** O aparelho não decide quem entra: a
   Bruna pode abrir a agenda no celular, e o Vitor pode abrir as tatuagens dele no computador. As
   telas não podem quebrar em nenhum dos dois tamanhos.
2. **O aparelho de cada perfil diz onde a tela precisa estar impecável.** Telas 1 e 2 são desenhadas
   para a tela pequena do celular; telas 3 e 4, para a tela grande do computador. A agenda é a que
   mais sofre se eu só esticar: filtro e lista precisam caber sem corte.

## 6. O que não faz parte

Fica fora, de propósito, para o escopo não estourar:

- orçamento e sinal
- pagamento
- portfólio com fotos
- aviso por mensagem

Nenhum desses quatro aparece no sistema. Se alguém pedir, a resposta é que não está no escopo da
cartilha.

## 7. O que eu já decidi, e o que falta

Nenhum destes pontos pode ser combinado com o colega de cartilha.

Já decidi:

- **os nomes das rotas da API.** São `/tatuagens` e `/tatuagens/{tatuagem_id}/passos`, e os status
  `pedida`, `desenho aprovado`, `em sessões` e `finalizada` são os da cartilha. O caminho aninhado
  dos passos existe porque um passo sem tatuagem dona não tem onde ficar.
- **de onde sai a lista de perfis.** Ela fica fixa no front, com os dois perfis do sistema: **Bruna,
  cliente**, e **Vitor, tatuador e dono do Traço Fino**. Não entra rota de usuário no back, porque a
  cartilha não pede isso e o perfil já é escolhido na tela, sem senha. O tipo de cada um viaja junto
  com o id: a Bruna manda o `cliente_id` dela no pedido, e o Vitor não manda nada disso.
- **de onde sai o nome da cliente.** A agenda do Vitor precisa mostrar de quem é cada tatuagem, e o
  nome mora no back, em `repositorios/cliente.py`, entrando na resposta como `nome_da_cliente`. A
  cartilha lista o usuário como uma das três entidades, e nome é dado do negócio: se o nome ficasse
  no front, o mesmo dado estaria escrito em dois lugares e divergiria na primeira correção. Esse
  depósito **não tem rota**, porque a cartilha não pede rota de cliente, e as cinco capacidades
  continuam sendo cinco.
- **a marca.** "Traço Fino" numa serifada de contraste alto, com uma linha fina de 1,5 px
  embaixo, na cor de acento. É uma palavra e uma linha: sem agulha, sem tribo. As quatro versões
  do logo estão em `docs/marca/`, e o que a marca é e as regras de uso estão em `docs/marca.md`.
- **onde a marca mora.** Os arquivos da marca não são copiados para o front. O Vite serve
  `docs/marca/` como arquivo estático, com `publicDir` em `frontend/vite.config.js`, e o cabeçalho
  das telas pede `/logo.svg`. Uma cópia dentro do front daria dois arquivos iguais no Git, e na
  primeira vez que o logo mudasse a cópia ficaria velha sem ninguém perceber.
- **a paleta e a tipografia.** Preto, branco e **uma** cor de acento, `#C2410C`, que é a única cor
  da interface além do preto e do branco. Corpo em sans-serif do sistema; logo e títulos em
  Playfair Display, com queda para Georgia. Os contrastes foram calculados e estão no styleguide,
  em `docs/styleguide/`.
- **a fonte fica no repositório, e não em link.** A Playfair Display foi baixada para
  `frontend/src/fontes/playfair-display.woff2`, 38 KB, e é declarada com `@font-face` em
  `tokens.css`. Podia ter sido um link do Google Fonts e seria uma linha a menos, mas aí a
  apresentação depende de internet, e a fonte de título é a assinatura do sistema. O
  `LEIA-ME.md` da pasta registra a origem e a licença, que é a SIL Open Font License 1.1.
- **a letra do logo está em curva.** Os quatro SVG da marca têm a palavra, e as letras do símbolo,
  desenhadas como `<path>`. Não por gosto de vetor: um SVG aberto com `<img>` é um documento
  separado e não enxerga a fonte que a página carregou, então a letra escrita como texto só
  apareceria igual nas máquinas com a Playfair Display instalada. O favicon é o pior caso, porque
  o navegador desenha o ícone sem fonte nenhuma.
- **tema claro e escuro.** O botão no cabeçalho alterna, e a escolha fica guardada no navegador.
  Quem nunca escolheu vê o tema do sistema operacional, respeitado na primeira pintura da página,
  sem piscar. O escuro não é o claro invertido: ele repete preto, branco e o mesmo laranja, com
  valores próprios porque contraste é o que impede texto de sumir. Uma coisa mudou de matiz: o
  laranja continua o mesmo quando é preenchimento, mas quando é **texto** — e a mensagem de erro
  da ficha é o caso — ele fica mais claro no escuro, porque `#C2410C` sobre `#111111` dá 3,65:1 e
  reprova. Os números estão no styleguide.
- **o logo troca de arquivo com o tema, e não de cor.** No escuro a interface pede o
  `logo-escuro.svg`, que já foi desenhado com a palavra em branco. Recolorir o logo por CSS seria
  uma versão da marca que ninguém desenhou, e a `marca.md` é explícita em não trocar as cores dele.

- **o comprimento da linha do logo.** A palavra cresceu de 40 para 46 de tamanho, e a linha foi
  encurtada para passar exatamente da primeira letra à última. Antes a palavra ocupava 207 px e a
  linha ia de 8 a 312, sobrando 98 px de linha solta depois do desenho, o que não é sublinhado.
  Agora a palavra ocupa 233 px e a linha vai de 9,3 a 242,6. A caixa do SVG encolheu de 320×72 para
  250×71, acompanhando a palavra, e a espessura da linha continua 1,5 px. O símbolo não mudou:
  ele é a versão para 32 pixels e não acompanha a palavra.

Ainda falta decidir, e continua sendo decisão de marca: o manual em PDF e o Figma da marca, que
estão anotados no fim de `docs/marca.md`.

## 8. Resumo objetivo

- **Regra:** a tatuagem nasce `pedida` e só anda por `desenho aprovado` → `sessão` → `retoque`,
  nessa ordem. Sessão antes do desenho aprovado é recusada. Retoque antes de pelo menos uma sessão é
  recusado. Cada passo aceito muda a etapa.
- **Quatro telas:** Pedir tatuagem, Minhas tatuagens, A agenda, A ficha. As duas primeiras do
  celular, as duas últimas do computador, todas responsivas.
- **Quem usa:** Bruna é a cliente, e usa o celular. Vitor é o tatuador e o dono, e usa o
  computador. As telas 1 e 2 são da Bruna, as telas 3 e 4 são do Vitor.
- **Três entidades:** usuário (cliente ou tatuador), tatuagem (pertence a um cliente) e passo
  (pertence a uma tatuagem).
- **Fora de escopo:** orçamento, sinal, pagamento, portfólio e aviso por mensagem.
- **Sem senha:** enquanto o login não chega, o perfil é escolhido numa lista, sem senha, e a tela da
  pessoa diz quem ela é na própria requisição.
