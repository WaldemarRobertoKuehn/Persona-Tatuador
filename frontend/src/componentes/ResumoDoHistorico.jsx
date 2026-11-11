/* Oferecer um rascunho editável do histórico sem gravá-lo no banco. */

import { useState } from "react";

import { gerarResumoIA } from "../api";

/* Mostrar espera, erro, edição e confirmação local do rascunho. */
export default function ResumoDoHistorico({ tatuagemId }) {
  const [carregando, setCarregando] = useState(false);
  const [rascunho, setRascunho] = useState("");
  const [erro, setErro] = useState("");
  const [revisado, setRevisado] = useState(false);

  /* Pedir um rascunho novo e manter a falha visível para permitir nova tentativa. */
  function solicitarResumo() {
    setCarregando(true);
    setErro("");
    setRevisado(false);

    gerarResumoIA(tatuagemId)
      .then((resposta) => {
        if (typeof resposta.rascunho !== "string" || !resposta.rascunho.trim()) {
          throw new Error("A IA não devolveu um rascunho para revisar.");
        }

        setRascunho(resposta.rascunho);
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
      })
      .finally(() => setCarregando(false));
  }

  /* Renderizar o editor apenas depois que a API entregar um rascunho válido. */
  return (
    <section className="resumo-ia" aria-labelledby={`titulo-resumo-${tatuagemId}`}>
      <h3 id={`titulo-resumo-${tatuagemId}`}>Resumo do histórico</h3>
      <p className="legenda">
        O texto é um rascunho da IA. Revisar e editar antes de usar; confirmar
        aqui não grava nada no sistema.
      </p>

      <div className="resumo-ia__acoes">
        {!rascunho || erro ? (
          <button
            type="button"
            className="botao-neutro"
            onClick={solicitarResumo}
            disabled={carregando}
          >
            {carregando
              ? "Gerando resumo..."
              : erro
                ? "Tentar novamente"
                : "Gerar resumo com IA"}
          </button>
        ) : null}
      </div>

      {carregando ? (
        <p className="aviso" role="status">
          A IA está preparando um rascunho. O histórico continua disponível.
        </p>
      ) : null}

      {erro ? (
        <p className="mensagem-erro" role="alert">
          {erro}
        </p>
      ) : null}

      {rascunho && !erro ? (
        <>
          <label className="campo">
            <span>Rascunho editável</span>
            <textarea
              value={rascunho}
              onChange={(evento) => {
                setRascunho(evento.target.value);
                setRevisado(false);
              }}
              rows={5}
            />
          </label>

          <div className="resumo-ia__acoes">
            <button
              type="button"
              className="botao"
              onClick={() => setRevisado(true)}
              disabled={!rascunho.trim() || revisado}
            >
              {revisado ? "Revisão confirmada" : "Confirmar revisão"}
            </button>
          </div>
        </>
      ) : null}

      {revisado ? (
        <p className="confirmacao" role="status">
          Rascunho revisado nesta tela; não foi gravado no banco.
        </p>
      ) : null}
    </section>
  );
}
