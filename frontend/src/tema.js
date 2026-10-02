/* O tema da tela, em um lugar só.
 *
 * São três decisões aqui. A primeira é como o tema é guardado: no atributo
 * data-tema do <html>, e não em um estado do React, porque quem decide a cor é o
 * CSS, e o React só precisa mandar o valor. A segunda é onde o valor fica
 * guardado entre uma visita e outra: no localStorage do navegador. A terceira é
 * que o estado do tema vive aqui, e não em cada tela, porque o botão fica no
 * cabeçalho, que é compartilhado pelas cinco telas.
 *
 * Sobre o atributo, e não sobre o estado do React: o CSS precisa saber o tema
 * antes do primeiro desenho da página. Se a cor viesse de um estado do React,
 * haveria um instante em que a tela já teria aparecido na cor antiga e o tema
 * novo ainda não teria chegado. Por isso o index.html tem um script no <head>
 * que aplica o tema antes de o React começar, e este módulo não repete essa
 * decisão: ele lê o atributo que aquele script deixou.
 */

import { useState } from "react";

const CHAVE = "tema";

export const CLARO = "claro";
export const ESCURO = "escuro";

/* O tema do sistema da pessoa, para o caso de o atributo não existir. Na prática
 * ele sempre existe, porque o script do index.html o aplica na abertura. O
 * matchMedia é o mesmo que o Windows e o celular usam para a tela escura do
 * sistema, então quem não escolheu nada vê o sistema respeitado. */
function temaDoSistema() {
  if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return ESCURO;
  }
  return CLARO;
}

/* O tema que está valendo agora, lido do atributo que o index.html aplicou. */
export function temaAtual() {
  const atributo = document.documentElement.getAttribute("data-tema");
  if (atributo === ESCURO) {
    return ESCURO;
  }
  if (atributo === CLARO) {
    return CLARO;
  }
  return temaDoSistema();
}

/* Troca o tema e lembra da escolha. Aplicar e guardar são o mesmo passo de
 * propósito: se guardasse antes de aplicar e a página fechasse no meio, o valor
 * ficaria salvo sem nunca ter aparecido na tela. */
function escolherTema(tema) {
  document.documentElement.setAttribute("data-tema", tema);
  window.localStorage.setItem(CHAVE, tema);
}

/* O estado do tema para as telas.
 *
 * O nome começa com "use" em inglês, e essa é a única vez que um nome deste
 * projeto não é em português. Não é gosto: o React identifica os próprios
 * ganchos pelo nome, e um gancho chamado "usarTema" o React não reconhece como
 * gancho. A regra do React ganha da regra do português neste ponto, e o resto do
 * projeto continua em português. */
export function useTema() {
  const [tema, guardarTema] = useState(temaAtual);

  function trocarTema(novo) {
    escolherTema(novo);
    guardarTema(novo);
  }

  return { tema, trocarTema };
}
