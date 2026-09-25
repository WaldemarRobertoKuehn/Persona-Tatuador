/* Os dois avisos da tela, que são dois dos três estados.
 *
 * Toda tela que chama o back passa por três estados: carregando, erro e pronto.
 * Este arquivo tem os dois primeiros, porque o terceiro é a própria tela. Usar
 * o mesmo componente nos dois avisos garante que o carregando e o erro tenham a
 * mesma cara em todas as quatro telas.
 */

export function AvisoCarregando({ oQue }) {
  return <p className="aviso">Carregando {oQue}...</p>;
}

export function AvisoErro({ erro }) {
  /* O texto do erro é o que o back mandou no detalhe. No caso da regra da
   * cartilha recusar um passo, esse texto é o motivo da recusa, escrito pelo
   * serviço, e é ele que o tatuador lê. */
  return (
    <p className="aviso aviso-erro" role="alert">
      {erro}
    </p>
  );
}

export function AvisoVazio({ children }) {
  return <p className="vazio">{children}</p>;
}
