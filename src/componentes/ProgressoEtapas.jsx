/* Indicador Visual do Ciclo da Tatuagem (Cartilha 4)
 * Mostra a linha do tempo da tatuagem pelas quatro etapas fundamentais:
 * 1. pedida -> 2. desenho aprovado -> 3. em sessões -> 4. finalizada
 */

const ORDEM_ETAPAS = ["pedida", "desenho aprovado", "em sessões", "finalizada"];

const NOMES_ETAPAS = {
  pedida: "Pedida",
  "desenho aprovado": "Desenho",
  "em sessões": "Sessões",
  finalizada: "Finalizada",
};

export default function ProgressoEtapas({ etapa }) {
  const indiceAtual = ORDEM_ETAPAS.indexOf(etapa);
  const progressoPercentual =
    indiceAtual >= 0 ? (indiceAtual / (ORDEM_ETAPAS.length - 1)) * 100 : 0;

  return (
    <div className="progresso-etapas" role="progressbar" aria-label={`Etapa atual: ${etapa}`}>
      <div className="progresso-linha" />
      <div
        className="progresso-linha-ativa"
        style={{ width: `calc(${progressoPercentual}% - 1.5rem)` }}
      />

      {ORDEM_ETAPAS.map((nome, index) => {
        const completo = index < indiceAtual;
        const atual = index === indiceAtual;

        return (
          <div
            key={nome}
            className={`progresso-ponto-bloco ${completo ? "completo" : ""} ${atual ? "atual" : ""}`}
          >
            <div className="progresso-marcador">
              {completo ? "✓" : index + 1}
            </div>
            <span className="progresso-texto">{NOMES_ETAPAS[nome]}</span>
          </div>
        );
      })}
    </div>
  );
}
