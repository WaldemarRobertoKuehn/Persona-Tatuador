/* Simular e explicar cada etapa de um atendimento fictício do estúdio. */

import { useState } from "react";

import { simularAtendimentoStudio } from "../api";

const PERSONAS = ["Cliente", "Atendente", "Tatuador(a)", "Administrador(a)"];

export default function SimulacaoDoStudio() {
  const [situacao, setSituacao] = useState("");
  const [etapas, setEtapas] = useState([]);
  const [simulando, setSimulando] = useState(false);
  const [erro, setErro] = useState("");

  function enviar(evento) {
    evento.preventDefault();
    setSimulando(true);
    setErro("");
    setEtapas([]);

    simularAtendimentoStudio(situacao)
      .then((resposta) => {
        if (
          !Array.isArray(resposta.etapas) ||
          resposta.etapas.length !== PERSONAS.length ||
          resposta.etapas.some(
            (etapa, indice) =>
              etapa.etapa !== indice + 1 ||
              etapa.persona !== PERSONAS[indice] ||
              !etapa.resumo?.trim() ||
              !etapa.fala?.trim(),
          )
        ) {
          throw new Error("A simulação voltou incompleta. Tente novamente.");
        }
        setEtapas(resposta.etapas);
      })
      .catch((erroRecebido) => setErro(erroRecebido.message))
      .finally(() => setSimulando(false));
  }

  return (
    <section className="cartao simulacao-studio">
      <h2>Simulação de atendimento com IA</h2>
      <p className="legenda legenda-folgada">
        Acompanhe um caso fictício pelas quatro personas: cliente, atendente,
        tatuador(a) e administrador(a). Cada etapa traz um resumo do que está
        acontecendo e a fala da persona.
      </p>

      <form className="formulario-de-equipe" onSubmit={enviar}>
        <label className="campo">
          <span>Situação hipotética</span>
          <textarea
            value={situacao}
            onChange={(evento) => setSituacao(evento.target.value)}
            minLength={10}
            maxLength={1500}
            rows={4}
            placeholder="Ex.: Cliente quer uma tatuagem floral pequena no antebraço e está em dúvida sobre o estilo."
            required
          />
        </label>
        <p className="legenda">
          Não inclua nomes, contatos ou informações pessoais. O texto será
          enviado ao provedor de IA e não será salvo nem usado para alterar a
          agenda, os pedidos ou os registros do estúdio.
        </p>

        {erro ? (
          <p className="mensagem-erro" role="alert">
            {erro}
          </p>
        ) : null}

        <button
          type="submit"
          className="botao"
          disabled={simulando || situacao.trim().length < 10}
        >
          {simulando ? "Simulando as quatro etapas..." : "Iniciar simulação"}
        </button>
      </form>

      {simulando ? (
        <p className="aviso" role="status">
          As personas estão conversando em sequência. Nenhum dado real está
          sendo alterado.
        </p>
      ) : null}

      {etapas.length > 0 ? (
        <ol className="etapas-simulacao">
          {etapas.map((etapa) => (
            <li className="etapa-simulacao" key={etapa.etapa}>
              <span className="etapa-simulacao__numero">
                Etapa {etapa.etapa} · {etapa.persona}
              </span>
              <h3>{etapa.titulo}</h3>
              <p>
                <strong>O que está acontecendo:</strong> {etapa.resumo}
              </p>
              <blockquote>{etapa.fala}</blockquote>
            </li>
          ))}
        </ol>
      ) : null}
    </section>
  );
}
