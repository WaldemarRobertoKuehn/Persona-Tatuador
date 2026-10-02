/* Tela 3 da cartilha: A agenda, do Vitor, no computador e celular. */

import { useEffect, useState } from "react";

import { buscarTatuagens } from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import Etiqueta from "../componentes/Etiqueta";

const ETAPAS = ["pedida", "desenho aprovado", "em sessões", "finalizada"];

export default function Agenda({ aoAbrirFicha }) {
  const [etapa, setEtapa] = useState("");
  const [estado, setEstado] = useState("carregando");
  const [tatuagens, setTatuagens] = useState([]);
  const [todasTatuagens, setTodasTatuagens] = useState([]);
  const [erro, setErro] = useState("");

  // Busca inicial de todas as tatuagens para métricas e contagens
  useEffect(() => {
    buscarTatuagens()
      .then((dados) => {
        setTodasTatuagens(dados);
      })
      .catch(() => {});
  }, []);

  // Busca com filtro por etapa no backend
  useEffect(() => {
    setEstado("carregando");
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

  const contagens = {
    total: todasTatuagens.length,
    pedida: todasTatuagens.filter((t) => t.etapa === "pedida").length,
    "desenho aprovado": todasTatuagens.filter((t) => t.etapa === "desenho aprovado").length,
    "em sessões": todasTatuagens.filter((t) => t.etapa === "em sessões").length,
    finalizada: todasTatuagens.filter((t) => t.etapa === "finalizada").length,
  };

  return (
    <main className="tela">
      <header className="cabecalho-secao">
        <div className="cabecalho-secao-topo">
          <div>
            <h1>A Agenda do Estúdio</h1>
            <p className="subtitulo-secao">
              Painel operacional do Vitor · Acompanhamento de projetos por etapa e acesso à ficha de sessão.
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.8125rem", color: "var(--cor-texto-fraco)" }}>
              Total: <strong>{contagens.total} tatuagens</strong>
            </span>
          </div>
        </div>
      </header>

      {/* Barra de Abas de Filtro com Contadores */}
      <div className="abas" role="group" aria-label="Filtrar por etapa">
        <button
          type="button"
          className={`aba-item ${etapa === "" ? "aba-ativa" : ""}`}
          onClick={() => setEtapa("")}
        >
          <span>Todas</span>
          <span className="aba-contador">{contagens.total}</span>
        </button>

        {ETAPAS.map((nome) => (
          <button
            key={nome}
            type="button"
            className={`aba-item ${etapa === nome ? "aba-ativa" : ""}`}
            onClick={() => setEtapa(nome)}
          >
            <span>{nome}</span>
            <span className="aba-contador">{contagens[nome] || 0}</span>
          </button>
        ))}
      </div>

      {estado === "carregando" ? <AvisoCarregando oQue="a agenda do estúdio" /> : null}
      {estado === "erro" ? <AvisoErro erro={erro} /> : null}

      {estado === "pronto" ? (
        tatuagens.length === 0 ? (
          <AvisoVazio>Nenhuma tatuagem registrada nesta etapa no momento.</AvisoVazio>
        ) : (
          <div className="tabela-container">
            <table className="tabela">
              <thead>
                <tr>
                  <th scope="col">Etapa</th>
                  <th scope="col">Ideia / Descrição</th>
                  <th scope="col">Local</th>
                  <th scope="col">Tamanho</th>
                  <th scope="col">Cliente</th>
                  <th scope="col" style={{ textAlign: "right" }}>Ação</th>
                </tr>
              </thead>

              <tbody>
                {tatuagens.map((tatuagem) => (
                  <tr key={tatuagem.id}>
                    <td data-rotulo="Etapa">
                      <Etiqueta etapa={tatuagem.etapa} />
                    </td>
                    <td data-rotulo="Ideia" style={{ fontWeight: 500, color: "var(--cor-texto)" }}>
                      {tatuagem.ideia}
                    </td>
                    <td data-rotulo="Local" style={{ color: "var(--cor-texto-medio)" }}>
                      {tatuagem.local_do_corpo}
                    </td>
                    <td data-rotulo="Tamanho" className="tabela-num" style={{ color: "var(--cor-texto-medio)" }}>
                      {tatuagem.tamanho} cm
                    </td>
                    <td data-rotulo="Cliente" style={{ fontWeight: 600 }}>
                      {tatuagem.nome_da_cliente}
                    </td>
                    <td data-rotulo="" style={{ textAlign: "right" }}>
                      <button
                        type="button"
                        className="botao-neutro botao-sm"
                        onClick={() => aoAbrirFicha(tatuagem)}
                        title={`Abrir ficha da tatuagem de ${tatuagem.nome_da_cliente}`}
                      >
                        Abrir ficha →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      ) : null}
    </main>
  );
}
