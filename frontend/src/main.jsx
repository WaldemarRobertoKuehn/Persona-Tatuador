/* O ponto de entrada do React. Não muda em relação ao que o Vite criou: o que
 * entra aqui é só o App, e o CSS.
 *
 * Os dois estilos são importados nesta ordem, e a ordem importa: tokens.css
 * primeiro, porque base.css usa as variáveis que ficam lá. Se base.css entrasse
 * antes, o navegador leria as cores como vazias.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./estilos/tokens.css";
import "./estilos/base.css";
import App from "./App.jsx";

/* getElementById("root") é o <div id="root"> do index.html. O React troca esse
 * div pelo que o App devolve, e é assim que a tela aparece no navegador. */
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
