/* Alternador de Tema Claro / Escuro */

import { ESCURO } from "../tema";

export default function AlternadorTema({ tema, trocarTema }) {
  const escuroAgora = tema === ESCURO;

  return (
    <button
      type="button"
      className="botao-neutro botao-sm"
      aria-pressed={escuroAgora}
      aria-label={escuroAgora ? "Mudar para tema claro" : "Mudar para tema escuro"}
      onClick={() => trocarTema(escuroAgora ? "claro" : "escuro")}
      title={escuroAgora ? "Mudar para tema claro" : "Mudar para tema escuro"}
    >
      <span aria-hidden="true">{escuroAgora ? "☼" : "☾"}</span>
      <span>{escuroAgora ? "Claro" : "Escuro"}</span>
    </button>
  );
}
