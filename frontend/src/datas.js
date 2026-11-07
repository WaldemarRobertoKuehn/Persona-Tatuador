/* O formato das datas na tela.
 *
 * O back devolve a data no formato ISO, "2026-09-25". Isso é o formato certo para
 * a API: ele não muda de significado com o idioma nem com o fuso horário do
 * navegador, e é o que uma máquina entende sem perguntar nada.
 *
 * Mas a tela é lida por gente, e gente no Brasil escreve dia antes de mês. Por
 * isso a conversão é aqui, e não no back: o back devolve o dado, e quem decide
 * como ele aparece é a tela.
 *
 * A conversão é feita com split, e não com o objeto Date, de propósito. O Date
 * entende "2026-09-25" como meia-noite em UTC, e o getDate() devolveria o dia
 * anterior em qualquer país a oeste de Greenwich, o que aqui no Brasil poderia
 * trocar o dia da tatuagem.
 */

export function formatarData(dataIso) {
  /* A data vazia devolve string vazia, e não um erro: quem formata é a tela, e a
   * tela não deve quebrar por causa de um campo que veio sem valor. */
  if (!dataIso) {
    return "";
  }

  /* O split quebra pelos hífens, e o destructuring nomeia as três partes na
   * ordem do formato ISO: ano, mês e dia. */
  const [ano, mes, dia] = dataIso.split("-");

  return `${dia}/${mes}/${ano}`;
}

/* Devolve a data de hoje no fuso do navegador, no formato ISO.
 *
 * toISOString não serve para isso: ele converte para UTC e, à noite no Brasil, o
 * dia já teria virado. A data montada com getFullYear, getMonth e getDate é a
 * data que a pessoa vê no calendário dela. */
export function dataLocalISO(data = new Date()) {
  const ano = data.getFullYear();
  const mes = String(data.getMonth() + 1).padStart(2, "0");
  const dia = String(data.getDate()).padStart(2, "0");

  return `${ano}-${mes}-${dia}`;
}

/* O back devolve o horário como "08:30:00". A tela mostra só "08:30". */
export function formatarHora(hora) {
  if (!hora) {
    return "";
  }

  return hora.slice(0, 5);
}
