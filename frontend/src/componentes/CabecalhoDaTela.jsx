/* O cabeçalho de uma tela: o que a tela é, e a ação principal dela.
 *
 * As quatro telas da cartilha têm o mesmo começo: um h1 que diz o que é a tela, uma
 * linha de apoio que diz de quem ela é, e uma ação. Só o que muda é o texto, então
 * isso é um componente, e não quatro cópias do mesmo cabeçalho.
 *
 * A ação fica à direita e não embaixo do título porque no computador sobra largura:
 * quem abre a tela já sabe onde a ação está, e ela não empurra o título para baixo.
 * No celular o flex-wrap do topo-do-cartao traz a ação para baixo do título, que é
 * a ordem de leitura: primeiro o que é a tela, depois o que dá para fazer nela.
 */

export default function CabecalhoDaTela({ titulo, apoio, acao }) {
  return (
    <header className="topo-do-cartao">
      <div>
        <h1>{titulo}</h1>
        {apoio ? <p className="legenda">{apoio}</p> : null}
      </div>

      {acao}
    </header>
  );
}