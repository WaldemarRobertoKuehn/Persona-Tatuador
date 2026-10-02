/* Etiqueta de Etapa da Tatuagem */

const CLASSES_DAS_ETAPAS = {
  pedida: "etiqueta-pedida",
  "desenho aprovado": "etiqueta-desenho",
  "em sessões": "etiqueta-sessoes",
  finalizada: "etiqueta-finalizada",
};

export default function Etiqueta({ etapa }) {
  const classe = CLASSES_DAS_ETAPAS[etapa] || "etiqueta-pedida";

  return (
    <span className={`etiqueta ${classe}`}>
      <span className="etiqueta-ponto" aria-hidden="true" />
      {etapa}
    </span>
  );
}
