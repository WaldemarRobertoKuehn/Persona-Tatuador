/* Tela 3 da cartilha: A agenda, do Vitor, no computador.
 *
 * A agenda é a tela que o Vitor abre primeiro, e é a que mais sofre se eu só
 * esticar: filtro e lista precisam caber sem corte. Por isso o filtro são abas
 * na horizontal e a lista é uma tabela com a coluna da cliente visível, como
 * manda o styleguide, seção 5.
 *
 * O filtro vai para o back, e não para o front. A rota já aceita etapa, e filtrar
 * no back é o que faz a agenda mostrar só o que interessa em vez de trazer tudo e
 * esconder. Quando o filtro muda, a busca roda de novo.
 *
 * O que a agenda NÃO faz é dizer o que pode ser feito em cada etapa. Isso é
 * chamar de regra, e a regra mora no serviço. A agenda mostra a etapa; quem sabe
 * o que acontece com um passo é a ficha, e quem recusa é o back.
 */

import { useEffect, useState } from "react";

import { buscarTatuagens } from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import Etiqueta from "../componentes/Etiqueta";

/* As quatro etapas da cartilha, na ordem em que a tatuagem anda. Esta lista
 * serve para desenhar as abas, e não para decidir o que é aceito: quem decide
 * isso é a regra do serviço, no back. */
const ETAPAS = ["pedida", "desenho aprovado", "em sessões", "finalizada"];

/* O botão que abre a ficha da tatuagem. A agenda não tem formulário: ela só
 * entrega a tatuagem escolhida para a ficha, e quem guarda essa escolha é o App. */
function BotaoDaFicha({ tatuagem, aoAbrir }) {
  return (
    <button
      type="button"
      className="botao-neutro"
      onClick={() => aoAbrir(tatuagem)}
    >
      Abrir ficha
    </button>
  );
}

export default function Agenda({ aoAbrirFicha }) {
  /* etapa começa vazia, e vazia é "todas". Guardar a etapa no estado é o que faz
   * o filtro ser do back: cada mudança deste estado dispara a busca de novo. */
  const [etapa, setEtapa] = useState("");
  const [estado, setEstado] = useState("carregando");
  const [tatuagens, setTatuagens] = useState([]);
  const [erro, setErro] = useState("");

  /* A busca depende só da etapa. Trocar de etapa é o único motivo para a agenda
   * buscar de novo, e é por isso que o id da tatuagem não entra aqui. */
  useEffect(() => {
    buscarTatuagens({ etapa: etapa || undefined })
      .then((dados) => {
        setTatuagens(dados);
        setEstado("pronto");
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEstado("erro");
      });
  }, [etapa]);

  return (
    <main className="tela">
      <header className="cabecalho">
        <h1>A agenda</h1>
        <p>todas as tatuagens do estúdio</p>
      </header>

      {/* A aba "Todas" é a que devolve a etapa vazia ao estado, que é como o back
          entende "sem filtro". As quatro outras são as etapas, na ordem da
          cartilha. */}
      <div className="abas" role="group" aria-label="Filtrar por etapa">
        <button
          type="button"
          className={etapa === "" ? "botao-neutro aba-ativa" : "botao-neutro"}
          onClick={() => setEtapa("")}
        >
          Todas
        </button>

        {ETAPAS.map((nome) => (
          <button
            key={nome}
            type="button"
            className={etapa === nome ? "botao-neutro aba-ativa" : "botao-neutro"}
            onClick={() => setEtapa(nome)}
          >
            {nome}
          </button>
        ))}
      </div>

      {estado === "carregando" ? <AvisoCarregando oQue="a agenda" /> : null}
      {estado === "erro" ? <AvisoErro erro={erro} /> : null}

      {estado === "pronto" ? (
        tatuagens.length === 0 ? (
          <AvisoVazio>Nenhuma tatuagem nesta etapa.</AvisoVazio>
        ) : (
          <table className="tabela">
            {/* O cabeçalho fica escondido da vista no celular, mas continua no
                documento: no celular quem diz o que é cada linha é o data-rotulo
                de cada célula. */}
            <thead className="so-leitor">
              <tr>
                <th scope="col">Etapa</th>
                <th scope="col">Ideia</th>
                <th scope="col">Local</th>
                <th scope="col">Tamanho</th>
                <th scope="col">Cliente</th>
                <th scope="col">Ficha</th>
              </tr>
            </thead>

            <tbody>
              {tatuagens.map((tatuagem) => (
                <tr key={tatuagem.id}>
                  {/* O data-rotulo é o nome da coluna, e só o CSS do celular usa
                      ele. No computador o nome vem do thead. */}
                  <td data-rotulo="Etapa">
                    <Etiqueta etapa={tatuagem.etapa} />
                  </td>
                  <td data-rotulo="Ideia">{tatuagem.ideia}</td>
                  <td data-rotulo="Local">{tatuagem.local_do_corpo}</td>
                  <td data-rotulo="Tamanho">{tatuagem.tamanho} cm</td>
                  <td data-rotulo="Cliente">{tatuagem.nome_da_cliente}</td>
                  <td data-rotulo="">
                    <BotaoDaFicha tatuagem={tatuagem} aoAbrir={aoAbrirFicha} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )
      ) : null}
    </main>
  );
}
