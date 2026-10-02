/* Tela 2 da cartilha: Minhas tatuagens, da Bruna, no celular e desktop. */

import { useEffect, useState } from "react";

import { buscarPassos, buscarTatuagens } from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import Etiqueta from "../componentes/Etiqueta";
import ProgressoEtapas from "../componentes/ProgressoEtapas";
import { formatarData } from "../datas";

function Historico({ tatuagemId }) {
  const [estado, setEstado] = useState("carregando");
  const [passos, setPassos] = useState([]);
  const [erro, setErro] = useState("");

  useEffect(() => {
    buscarPassos(tatuagemId)
      .then((dados) => {
        setPassos(dados);
        setEstado("pronto");
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEstado("erro");
      });
  }, [tatuagemId]);

  if (estado === "carregando") {
    return <AvisoCarregando oQue="o histórico dos passos" />;
  }

  if (estado === "erro") {
    return <AvisoErro erro={erro} />;
  }

  if (passos.length === 0) {
    return (
      <div className="aviso" style={{ marginTop: "1rem" }}>
        Nenhum passo registrado ainda. Sua ideia foi recebida e está aguardando a aprovação do desenho pelo Vitor.
      </div>
    );
  }

  return (
    <div style={{ marginTop: "1.25rem", borderTop: "1px solid var(--cor-borda-suave)", paddingTop: "1rem" }}>
      <h4 style={{ fontSize: "0.875rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--cor-texto-fraco)", marginBottom: "0.75rem" }}>
        Histórico de Etapas Concluídas ({passos.length})
      </h4>
      <ul className="timeline">
        {passos.map((passo) => (
          <li key={passo.id} className="timeline-item">
            <span className="timeline-ponto" aria-hidden="true" />
            <div className="timeline-conteudo">
              <div className="timeline-topo">
                <span className="timeline-tipo">{passo.tipo}</span>
                <span className="timeline-data">{formatarData(passo.data)}</span>
              </div>
              {passo.observacao ? (
                <p className="timeline-obs">{passo.observacao}</p>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function MinhasTatuagens({ perfil, aoAbrirPedido }) {
  const [estado, setEstado] = useState("carregando");
  const [tatuagens, setTatuagens] = useState([]);
  const [erro, setErro] = useState("");
  const [aberta, setAberta] = useState(null);

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
      <header className="cabecalho-secao">
        <div className="cabecalho-secao-topo">
          <div>
            <h1>Minhas Tatuagens</h1>
            <p className="subtitulo-secao">
              Olá, {perfil.nome}! Acompanhe aqui o andamento de cada projeto e histórico de sessões.
            </p>
          </div>
          <button type="button" className="botao" onClick={aoAbrirPedido}>
            + Pedir nova tatuagem
          </button>
        </div>
      </header>

      {estado === "carregando" ? <AvisoCarregando oQue="suas tatuagens" /> : null}
      {estado === "erro" ? <AvisoErro erro={erro} /> : null}

      {estado === "pronto" ? (
        tatuagens.length === 0 ? (
          <div className="cartao vazio">
            <h3>Nenhuma tatuagem pedida ainda</h3>
            <p style={{ marginTop: "0.5rem", maxWidth: "28rem", margin: "0.5rem auto 1.5rem" }}>
              Você ainda não enviou nenhum pedido de tatuagem para o estúdio. Conte a sua ideia para o Vitor avaliar e iniciar o desenho.
            </p>
            <button type="button" className="botao" onClick={aoAbrirPedido}>
              Pedir Minha Primeira Tatuagem
            </button>
          </div>
        ) : (
          <div style={{ display: "grid", gap: "1.25rem" }}>
            {tatuagens.map((tatuagem) => {
              const isAberta = aberta === tatuagem.id;

              return (
                <article key={tatuagem.id} className="cartao">
                  <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between", gap: "1rem" }}>
                    <div>
                      <h2 style={{ fontSize: "1.25rem", marginBottom: "0.375rem" }}>
                        {tatuagem.ideia}
                      </h2>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", fontSize: "0.8125rem", color: "var(--cor-texto-fraco)" }}>
                        <span>Local: <strong>{tatuagem.local_do_corpo}</strong></span>
                        <span aria-hidden="true">·</span>
                        <span style={{ fontVariantNumeric: "tabular-nums" }}>Tamanho: <strong>{tatuagem.tamanho} cm</strong></span>
                        <span aria-hidden="true">·</span>
                        <span>Código #{tatuagem.id}</span>
                      </div>
                    </div>
                    <Etiqueta etapa={tatuagem.etapa} />
                  </div>

                  {/* Visual 4-Step Milestone Progression */}
                  <ProgressoEtapas etapa={tatuagem.etapa} />

                  <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "0.75rem" }}>
                    <button
                      type="button"
                      className="botao-neutro botao-sm"
                      onClick={() => setAberta(isAberta ? null : tatuagem.id)}
                    >
                      {isAberta ? "Ocultar histórico ▲" : "Ver histórico de sessões ▼"}
                    </button>
                  </div>

                  {isAberta ? <Historico tatuagemId={tatuagem.id} /> : null}
                </article>
              );
            })}
          </div>
        )
      ) : null}
    </main>
  );
}
