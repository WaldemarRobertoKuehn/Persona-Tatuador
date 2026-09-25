/* A etiqueta de etapa.
 *
 * A etapa é a informação mais importante de uma tatuagem, e a cor dela vem da
 * tabela do styleguide. Este componente só decide qual classe usar; a cor está
 * nas variáveis do tokens.css.
 *
 * A prop classe serve para o mesmo texto virar cores diferentes: o nome da
 * etapa "em sessões" tem espaço e um acento, que não servem bem em nome de
 * classe, então quem chama passa o nome curto.
 */

const CLASSES_DAS_ETAPAS = {
  pedida: "etiqueta-pedida",
  "desenho aprovado": "etiqueta-desenho",
  "em sessões": "etiqueta-sessoes",
  finalizada: "etiqueta-finalizada",
};

export default function Etiqueta({ etapa }) {
  /* Se a etapa vier com um texto que o back ainda não conhece, o componente
   * mostra a etapa neutra em vez de quebrar a tela. Uma etapa desconhecida é
   * informação nova, e esconder isso seria pior do que mostrar sem cor. */
  const classe = CLASSES_DAS_ETAPAS[etapa] || "etiqueta-pedida";

  return <span className={`etiqueta ${classe}`}>{etapa}</span>;
}
