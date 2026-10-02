/* Tela 4 da cartilha: A ficha, do Vitor, no computador e celular. */

import { useEffect, useState } from "react";

import { buscarPassos, buscarTatuagem, registrarPasso } from "../api";
import { AvisoCarregando } from "../componentes/Avisos";
import Etiqueta from "../componentes/Etiqueta";
import ProgressoEtapas from "../componentes/ProgressoEtapas";
import { formatarData } from "../datas";

const TIPOS_DE_PASSO = [
  { valor: "desenho aprovado", rotulo: "desenho aprovado", regra: "Aceito se 'pedida' → muda para 'desenho aprovado'" },
  { valor: "sessão", rotulo: "sessão", regra: "Aceito se 'desenho aprovado' ou 'em sessões' → muda para 'em sessões'" },
  { valor: "retoque", rotulo: "retoque", regra: "Aceito se 'em sessões' → muda para 'finalizada'" },
];

export default function Ficha({ tatuagem, aoVoltarParaAgenda }) {
  const [etapaAtual, setEtapaAtual] = useState(tatuagem.etapa);
  const [passos, setPassos] = useState([]);
  const [passosDa, setPassosDa] = useState(null);
  const [tipo, setTipo] = useState("");
  const [observacao, setObservacao] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [confirmacao, setConfirmacao] = useState("");

  const carregando = passosDa !== tatuagem.id;

  useEffect(() => {
    let vivo = true;

    buscarPassos(tatuagem.id)
      .then((passosRecebidos) => {
        if (vivo) {
          setPassos(passosRecebidos);
        }
      })
      .catch((erroRecebido) => {
        if (vivo) {
          setErro(erroRecebido.message);
        }
      })
      .finally(() => {
        if (vivo) {
          setPassosDa(tatuagem.id);
        }
      });

    return () => {
      vivo = false;
    };
  }, [tatuagem.id]);

  function recarregar() {
    buscarTatuagem(tatuagem.id)
      .then((atualizada) => setEtapaAtual(atualizada.etapa))
      .catch((erroRecebido) => setErro(erroRecebido.message));

    buscarPassos(tatuagem.id)
      .then(setPassos)
      .catch((erroRecebido) => setErro(erroRecebido.message));
  }

  function enviar(evento) {
    evento.preventDefault();

    setEnviando(true);
    setErro("");
    setConfirmacao("");

    registrarPasso(tatuagem.id, { tipo, observacao })
      .then((passo) => {
        setConfirmacao(
          `Passo '${passo.tipo}' gravado com sucesso em ${formatarData(passo.data)}.`
        );
        setTipo("");
        setObservacao("");
        setEnviando(false);
        recarregar();
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEnviando(false);
      });
  }

  return (
    <main className="tela">
      <header className="cabecalho-secao">
        <div className="cabecalho-secao-topo">
          <div>
            <h1>Ficha da Tatuagem #{tatuagem.id}</h1>
            <p className="subtitulo-secao">
              Cliente: <strong>{tatuagem.nome_da_cliente}</strong> · Registro operacional e histórico de passos
            </p>
          </div>
          <button type="button" className="botao-neutro botao-sm" onClick={aoVoltarParaAgenda}>
            ← Voltar para a agenda
          </button>
        </div>
      </header>

      <div className="ficha-layout">
        {/* Coluna 1: Dossiê e Histórico da Tatuagem */}
        <section className="cartao">
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-start", justifyContent: "space-between", gap: "1rem" }}>
            <div>
              <h2 style={{ fontSize: "1.35rem", marginBottom: "0.375rem" }}>{tatuagem.ideia}</h2>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", fontSize: "0.8125rem", color: "var(--cor-texto-fraco)" }}>
                <span>Local: <strong>{tatuagem.local_do_corpo}</strong></span>
                <span aria-hidden="true">·</span>
                <span style={{ fontVariantNumeric: "tabular-nums" }}>Tamanho: <strong>{tatuagem.tamanho} cm</strong></span>
                <span aria-hidden="true">·</span>
                <span>Cliente: <strong>{tatuagem.nome_da_cliente}</strong></span>
              </div>
            </div>
            <Etiqueta etapa={etapaAtual} />
          </div>

          {/* Progresso de 4 Etapas */}
          <div style={{ margin: "1.5rem 0 1rem" }}>
            <ProgressoEtapas etapa={etapaAtual} />
          </div>

          {confirmacao ? (
            <div className="confirmacao" role="status">
              <strong style={{ color: "var(--cor-acento-texto)" }}>✓ Atualização:</strong>
              <span>{confirmacao}</span>
            </div>
          ) : null}

          <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--cor-borda-suave)", paddingTop: "1.25rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
              <h3 style={{ fontSize: "1rem" }}>Histórico de Passos Realizados</h3>
              <span style={{ fontSize: "0.75rem", color: "var(--cor-texto-fraco)" }}>
                {passos.length} {passos.length === 1 ? "registro" : "registros"}
              </span>
            </div>

            {carregando ? (
              <AvisoCarregando oQue="o histórico desta tatuagem" />
            ) : passos.length === 0 ? (
              <p className="vazio">Nenhum passo registrado ainda nesta ficha.</p>
            ) : (
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
            )}
          </div>
        </section>

        {/* Coluna 2: Formulário de Registro de Passo */}
        <section className="cartao">
          <h2 style={{ fontSize: "1.2rem", marginBottom: "0.5rem" }}>Registrar um Passo</h2>
          <p style={{ fontSize: "0.8125rem", color: "var(--cor-texto-fraco)", marginBottom: "1.25rem" }}>
            A regra da Cartilha 4 valida a transição de etapa no servidor.
          </p>

          <form onSubmit={enviar}>
            <label className="campo">
              <span>Tipo do Passo</span>
              <select
                name="tipo"
                value={tipo}
                onChange={(evento) => {
                  setTipo(evento.target.value);
                  setErro("");
                }}
                required
              >
                <option value="">Selecione o passo a registrar...</option>
                {TIPOS_DE_PASSO.map((item) => (
                  <option key={item.valor} value={item.valor}>
                    {item.rotulo}
                  </option>
                ))}
              </select>
            </label>

            {/* Dica da Regra da Cartilha para o Passo Selecionado */}
            {tipo ? (
              <div style={{ padding: "0.625rem 0.875rem", background: "var(--cor-superficie-suave)", border: "1px solid var(--cor-borda)", borderRadius: "var(--raio)", fontSize: "0.775rem", color: "var(--cor-texto-medio)", marginBottom: "1rem" }}>
                <strong>Regra:</strong> {TIPOS_DE_PASSO.find((t) => t.valor === tipo)?.regra}
              </div>
            ) : null}

            {erro ? (
              <div className="mensagem-erro" role="alert">
                <strong>Recusa da Regra:</strong>
                <p style={{ marginTop: "0.25rem" }}>{erro}</p>
              </div>
            ) : null}

            <label className="campo">
              <span>
                Observação do Passo (opcional)
                <span className="campo-dica">{observacao.length}/500</span>
              </span>
              <textarea
                name="observacao"
                value={observacao}
                onChange={(evento) => setObservacao(evento.target.value)}
                maxLength={500}
                placeholder="Ex.: Linha fina realizada com agulha 03RL, cliente tolerou bem a sessão."
              />
            </label>

            <button type="submit" className="botao" style={{ width: "100%" }} disabled={enviando}>
              {enviando ? "Registrando passo..." : "Registrar Passo e Atualizar Etapa"}
            </button>
          </form>

          {/* Guia das regras do estúdio */}
          <div style={{ marginTop: "1.5rem", borderTop: "1px solid var(--cor-borda-suave)", paddingTop: "1rem", fontSize: "0.775rem", color: "var(--cor-texto-fraco)" }}>
            <strong style={{ color: "var(--cor-texto)" }}>Regras da Cartilha 4:</strong>
            <ul style={{ paddingLeft: "1.1rem", margin: "0.375rem 0 0", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              <li><strong>Desenho aprovado</strong>: exige etapa 'pedida'.</li>
              <li><strong>Sessão</strong>: exige 'desenho aprovado' ou 'em sessões'.</li>
              <li><strong>Retoque</strong>: exige 'em sessões' (após cicatrização).</li>
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
