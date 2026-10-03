/* A linha do tempo dos passos de uma tatuagem.
 *
 * A mesma lista aparece em dois lugares: no histórico que a Bruna abre em "Minhas
 * tatuagens" e no histórico que o Vitor vê na ficha. Os dois mostram a mesma
 * informação — tipo do passo, data e observação —, então o desenho é um só, e cada
 * tela decide só quando busca e o que fazer quando não tem passo nenhum.
 *
 * O traço da esquerda é feito com o ::before do CSS, e não com um elemento da
 * lista: a lista é uma lista de passos, e um elemento a mais por passo seria um
 * elemento que o leitor de tela leria sem motivo.
 */

import { formatarData } from "../datas";

/* A linha do tempo propriamente dito. Ela recebe a lista de passos e não busca
 * nada: quem busca é a tela, porque só a tela sabe de qual tatuagem. */
export default function LinhaDoTempo({ passos }) {
  return (
    <ol className="linha-do-tempo">
      {passos.map((passo) => (
        <li key={passo.id} className="passo">
          {/* O ponto da régua. Ele é decorativo: o que importa é o tipo do
              passo e a data, que estão escritos na lista. */}
          <span className="passo-ponto" aria-hidden="true" />

          <div className="passo-conteudo">
            <div className="passo-topo">
              <span className="passo-tipo">{passo.tipo}</span>
              <span className="passo-data">{formatarData(passo.data)}</span>
            </div>

            {/* A observação é opcional porque o esquema do back não obriga a
                preenchê-la, e um passo sem observação continua sendo um passo
                registrado. */}
            {passo.observacao ? <p className="passo-observacao">{passo.observacao}</p> : null}
          </div>
        </li>
      ))}
    </ol>
  );
}