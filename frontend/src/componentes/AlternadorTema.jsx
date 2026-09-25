/* O botão que alterna o tema da tela.
 *
 * Ele fica no cabeçalho, ao lado do logo, e é a única coisa da tela que a pessoa
 * usa para mudar a cara do sistema inteiro. Aparece nas cinco telas, e por isso
 * vive em um componente só.
 *
 * O texto do botão diz o que vai acontecer, e não o que está valendo agora: quem
 * lê "escuro" com a tela clara entende que a tela vai ficar escura. Inverter a
 * lógica obriga a pessoa a lembrar o estado antes de ler a palavra.
 *
 * O aria-pressed é o que conta para o leitor de tela que o botão é um interruptor
 * e que ele está ligado. Sem ele, a pessoa ouve "escuro" e não sabe se o site
 * está escuro ou se o botão só oferece isso.
 *
 * O botão não guarda o tema: ele recebe de quem tem o estado, que é o useTema em
 * tema.js. Se ele guardasse, cada tela que o montasse teria o seu próprio tema,
 * e a pessoa teria um site com dois temas ao mesmo tempo.
 */

import { ESCURO } from "../tema";

export default function AlternadorTema({ tema, trocarTema }) {
  const escuroAgora = tema === ESCURO;

  return (
    <button
      type="button"
      className="botao-neutro alternador-tema"
      aria-pressed={escuroAgora}
      onClick={() => trocarTema(escuroAgora ? "claro" : "escuro")}
    >
      {escuroAgora ? "Tema claro" : "Tema escuro"}
    </button>
  );
}
