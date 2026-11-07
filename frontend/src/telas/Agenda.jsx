/* Tela 3 da cartilha: A agenda, do Vitor, no computador.
 *
 * A agenda é a tela que o Vitor abre primeiro, e é a que mais sofre se eu só
 * esticar: filtro e lista precisam caber sem corte. Por isso o filtro são abas
 * na horizontal e a lista é uma tabela com a coluna da cliente visível, como
 * manda o styleguide, seção 5.
 *
 * A agenda busca a lista uma única vez e filtra no front. A contagem das abas e a
 * lista mostrada saem da mesma resposta, então trocar de aba não dispara outra
 * consulta ao banco. Antes eram duas chamadas completas a cada abertura de tela.
 *
 * O que a agenda NÃO faz é dizer o que pode ser feito em cada etapa. Isso é
 * chamar de regra, e a regra mora no serviço. A agenda mostra a etapa; quem sabe
 * o que acontece com um passo é a ficha, e quem recusa é o back.
 */

import { useEffect, useState } from "react";

import { buscarTatuagens } from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import CabecalhoDaTela from "../componentes/CabecalhoDaTela";
import Etiqueta from "../componentes/Etiqueta";
import MiniaturaDoDesenho from "../componentes/MiniaturaDoDesenho";
import { ETAPAS } from "../perfis";

export default function Agenda({ aoAbrirFicha }) {
  /* etapa começa vazia, e vazia é "todas". */
  const [etapa, setEtapa] = useState("");
  const [estado, setEstado] = useState("carregando");
  const [todas, setTodas] = useState([]);
  const [erro, setErro] = useState("");

  /* Uma única busca ao abrir a tela. A contagem e a lista filtrada saem daqui. */
  useEffect(() => {
    buscarTatuagens()
      .then((dados) => {
        setTodas(dados);
        setEstado("pronto");
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEstado("erro");
      });
  }, []);

  const tatuagens = etapa
    ? todas.filter((tatuagem) => tatuagem.etapa === etapa)
    : todas;

  /* Quantas tatuagens existem em cada etapa. O forEach com filter é a mesma
   * contagem das cinco listas, e o objeto que começa com o total é o que faz uma
   * etapa sem tatuagem nenhuma mostrar 0 em vez de vazio. */
  const contagens = { total: todas.length };

  ETAPAS.forEach((nome) => {
    contagens[nome] = todas.filter((tatuagem) => tatuagem.etapa === nome).length;
  });

  return (
    <main className="tela">
      <CabecalhoDaTela
        titulo="A agenda"
        apoio={`${contagens.total} tatuagens do estúdio, com a etapa de cada uma.`}
      />

      {/* A aba "Todas" é a que devolve a etapa vazia ao estado, que é como o back
          entende "sem filtro". As quatro outras são as etapas, na ordem da
          cartilha. */}
      <div className="abas" role="group" aria-label="Filtrar por etapa">
        <button
          type="button"
          className={etapa === "" ? "botao-neutro aba-ativa" : "botao-neutro"}
          onClick={() => setEtapa("")}
        >
          Todas <span className="aba-conta">{contagens.total}</span>
        </button>

        {ETAPAS.map((nome) => (
          <button
            key={nome}
            type="button"
            className={etapa === nome ? "botao-neutro aba-ativa" : "botao-neutro"}
            onClick={() => setEtapa(nome)}
          >
            {nome} <span className="aba-conta">{contagens[nome]}</span>
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
                <th scope="col">Desenho</th>
                <th scope="col">Etapa</th>
                <th scope="col">Ideia</th>
                <th scope="col">Local</th>
                <th scope="col">Tamanho</th>
                <th scope="col">Cliente</th>
                <th scope="col">Tatuador</th>
                <th scope="col">Ficha</th>
              </tr>
            </thead>

            <tbody>
              {tatuagens.map((tatuagem) => (
                <tr key={tatuagem.id}>
                  {/* O data-rotulo é o nome da coluna, e só o CSS do celular usa
                      ele. No computador o nome vem do thead. */}
                  <td data-rotulo="Desenho">
                    <MiniaturaDoDesenho
                      tatuagemId={tatuagem.id}
                      imagemId={tatuagem.desenho_imagem_id}
                    />
                  </td>
                  <td data-rotulo="Etapa">
                    <Etiqueta etapa={tatuagem.etapa} />
                  </td>
                  <td data-rotulo="Ideia">{tatuagem.ideia}</td>
                  <td data-rotulo="Local">{tatuagem.local_do_corpo}</td>
                  <td data-rotulo="Tamanho" className="numero">
                    {tatuagem.tamanho} cm
                  </td>
                  <td data-rotulo="Cliente">{tatuagem.nome_da_cliente}</td>
                  <td data-rotulo="Tatuador">
                    {tatuagem.tatuador_nome ?? "Sem tatuador"}
                  </td>
                  <td data-rotulo="">
                    <button
                      type="button"
                      className="botao-neutro"
                      onClick={() => aoAbrirFicha(tatuagem)}
                    >
                      Abrir ficha
                    </button>
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