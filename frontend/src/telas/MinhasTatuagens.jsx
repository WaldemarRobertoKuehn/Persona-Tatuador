/* Tela 2 da cartilha: Minhas tatuagens, da Bruna, no celular.
 *
 * São duas coisas nesta tela: a lista das tatuagens dela, com a etapa de cada
 * uma, e o histórico de cada tatuagem, que é o que aparece quando ela abre uma.
 * As duas moram na mesma tela porque são a mesma pessoa olhando a mesma coisa.
 *
 * Os três estados da tela estão aqui: carregando, erro e pronto. O histórico de
 * uma tatuagem só é buscado quando a Bruna abre aquela tatuagem, e não junto com
 * a lista, porque ela raramente abre todas.
 */

import { useEffect, useState } from "react";

import { buscarPassos, buscarTatuagens } from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import Etiqueta from "../componentes/Etiqueta";
import { formatarData } from "../datas";

/* O histórico de uma tatuagem, buscado só quando a Bruna abre ela. */
function Historico({ tatuagemId }) {
  /* O estado dos três: começa carregando porque a busca só vai começar agora. */
  const [estado, setEstado] = useState("carregando");
  const [passos, setPassos] = useState([]);
  const [erro, setErro] = useState("");

  /* useEffect com o array de dependências é o que roda o código quando a tela
   * entra. O segundo argumento é a lista do que precisa mudar para rodar de
   * novo: aqui, só o id da tatuagem. */
  useEffect(() => {
    /* Chamada imperativa dentro do useEffect, porque buscar dado é trabalho de
     * efeito colateral: a tela monta primeiro e o dado chega depois. */
    buscarPassos(tatuagemId)
      .then((dados) => {
        setPassos(dados);
        setEstado("pronto");
      })
      /* O catch é obrigatório: sem ele, uma falha de rede vira promessa
       * rejeitada sem dono e a tela fica carregando para sempre. */
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEstado("erro");
      });
  }, [tatuagemId]);

  if (estado === "carregando") {
    return <AvisoCarregando oQue="o histórico" />;
  }

  if (estado === "erro") {
    return <AvisoErro erro={erro} />;
  }

  if (passos.length === 0) {
    return <AvisoVazio>Nenhum passo ainda. A tatuagem está esperando o desenho.</AvisoVazio>;
  }

  return (
    <ol className="lista">
      {passos.map((passo) => (
        <li key={passo.id} className="cartao">
          <strong>{passo.tipo}</strong> · {formatarData(passo.data)}
          {passo.observacao ? <p>{passo.observacao}</p> : null}
        </li>
      ))}
    </ol>
  );
}

export default function MinhasTatuagens({ perfil, aoAbrirPedido }) {
  const [estado, setEstado] = useState("carregando");
  const [tatuagens, setTatuagens] = useState([]);
  const [erro, setErro] = useState("");
  const [aberta, setAberta] = useState(null);

  /* O filtro de cliente vai na requisição, e ele é o id do perfil escolhido. É
   * por isso que a Bruna não vê a tatuagem de ninguém mais.
   *
   * O estado já nasce em carregando e o efeito não precisa voltar para
   * carregando: o efeito só roda de novo quando o id do perfil muda, e trocar de
   * perfil desmonta a tela, então o estado novo nasce limpo de qualquer jeito. */
  useEffect(() => {
    buscarTatuagens({ clienteId: perfil.id })
      .then((dados) => {
        setTatuagens(dados);
        setEstado("pronto");
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEstado("erro");
      });
  }, [perfil.id]);

  return (
    <main className="tela">
      <header className="cabecalho">
        <h1>Minhas tatuagens</h1>
        <p>{perfil.nome}</p>
      </header>

      <button type="button" className="botao" onClick={aoAbrirPedido}>
        Pedir tatuagem
      </button>

      {estado === "carregando" ? <AvisoCarregando oQue="suas tatuagens" /> : null}
      {estado === "erro" ? <AvisoErro erro={erro} /> : null}

      {estado === "pronto" ? (
        tatuagens.length === 0 ? (
          <AvisoVazio>Você ainda não tem tatuagem aqui.</AvisoVazio>
        ) : (
          <ul className="lista" style={{ marginTop: "1.5rem" }}>
            {tatuagens.map((tatuagem) => (
              <li key={tatuagem.id} className="cartao">
                <div className="cartao-tatuagem">
                  <div>
                    <h2>{tatuagem.ideia}</h2>
                    <p>
                      {tatuagem.local_do_corpo} · {tatuagem.tamanho} cm
                    </p>
                  </div>
                  <Etiqueta etapa={tatuagem.etapa} />
                </div>

                <button
                  type="button"
                  className="botao-neutro"
                  style={{ marginTop: "0.5rem" }}
                  onClick={() =>
                    setAberta(aberta === tatuagem.id ? null : tatuagem.id)
                  }
                >
                  {aberta === tatuagem.id ? "Fechar histórico" : "Ver histórico"}
                </button>

                {aberta === tatuagem.id ? (
                  <div style={{ marginTop: "0.5rem" }}>
                    <Historico tatuagemId={tatuagem.id} />
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )
      ) : null}
    </main>
  );
}
