/* Tela 1 da cartilha: Pedir tatuagem, da Bruna. */

import { useState } from "react";

import { criarTatuagem } from "../api";
import Etiqueta from "../componentes/Etiqueta";

const SUGESTOES = [
  "Ramo botânico de oliveira com traço fino e folhas delicadas",
  "Borboleta minimalista com micro-sombreamento",
  "Frase em caligrafia cursiva fina no antebraço",
  "Constelação delicada com pequenos pontos geométricos",
];

export default function PedirTatuagem({ perfil, aoConcluir }) {
  const [formulario, setFormulario] = useState({
    ideia: "",
    local_do_corpo: "",
    tamanho: "",
  });
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [foiGravado, setFoiGravado] = useState(false);

  function mudar(campo, valor) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function aplicarSugestao(texto) {
    setFormulario((anterior) => ({ ...anterior, ideia: texto }));
  }

  function enviar(evento) {
    evento.preventDefault();

    setEnviando(true);
    setErro("");
    setFoiGravado(false);

    criarTatuagem({
      cliente_id: perfil.id,
      ideia: formulario.ideia,
      local_do_corpo: formulario.local_do_corpo,
      tamanho: Number(formulario.tamanho),
    })
      .then(() => {
        setFormulario({ ideia: "", local_do_corpo: "", tamanho: "" });
        setFoiGravado(true);
        setEnviando(false);
      })
      .catch((erroRecebido) => {
        setErro(erroRecebido.message);
        setEnviando(false);
      });
  }

  return (
    <main className="tela" style={{ maxWidth: "56rem" }}>
      <header className="cabecalho-secao">
        <div className="cabecalho-secao-topo">
          <div>
            <h1>Pedir Nova Tatuagem</h1>
            <p className="subtitulo-secao">
              Descreva sua ideia para o Vitor. A tatuagem nascerá com o status inicial de <strong>pedida</strong>.
            </p>
          </div>
        </div>
      </header>

      {foiGravado ? (
        <div className="cartao" style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
          <div style={{ width: "48px", height: "48px", borderRadius: "50%", background: "var(--cor-acento-suave)", color: "var(--cor-acento-texto)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem", fontSize: "1.5rem" }}>
            ✓
          </div>
          <h2 style={{ marginBottom: "0.5rem" }}>Pedido Registrado com Sucesso!</h2>
          <p style={{ color: "var(--cor-texto-fraco)", maxWidth: "30rem", margin: "0 auto 1.5rem" }}>
            Sua ideia foi enviada e agora consta na agenda do estúdio como <strong>pedida</strong>. O Vitor analisará o conceito para elaborar e submeter o desenho para sua aprovação.
          </p>
          <div style={{ display: "flex", justifyContent: "center", gap: "1rem" }}>
            <button
              type="button"
              className="botao"
              onClick={aoConcluir}
            >
              Ver em Minhas Tatuagens
            </button>
            <button
              type="button"
              className="botao-neutro"
              onClick={() => setFoiGravado(false)}
            >
              Enviar Outro Pedido
            </button>
          </div>
        </div>
      ) : (
        <div className="ficha-layout">
          {/* Formulário Principal */}
          <form className="cartao" onSubmit={enviar}>
            <label className="campo">
              <span>
                Sua ideia de tatuagem
                <span className="campo-dica">Mínimo 10 caracteres</span>
              </span>
              <textarea
                name="ideia"
                value={formulario.ideia}
                onChange={(evento) => mudar("ideia", evento.target.value)}
                placeholder="Ex.: Ramo de cerejeira delicado no antebraço interno com traço ultrafino..."
                minLength={10}
                maxLength={500}
                required
              />
            </label>

            {/* Sugestões rápidas */}
            <div style={{ marginBottom: "1.25rem" }}>
              <span style={{ fontSize: "0.75rem", color: "var(--cor-texto-fraco)", display: "block", marginBottom: "0.375rem" }}>
                Inspirações do estúdio:
              </span>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem" }}>
                {SUGESTOES.map((sugestao, i) => (
                  <button
                    key={i}
                    type="button"
                    className="botao-neutro botao-sm"
                    style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem" }}
                    onClick={() => aplicarSugestao(sugestao)}
                  >
                    + {sugestao.slice(0, 32)}...
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <label className="campo">
                <span>Local no corpo</span>
                <input
                  name="local_do_corpo"
                  value={formulario.local_do_corpo}
                  onChange={(evento) => mudar("local_do_corpo", evento.target.value)}
                  placeholder="Ex.: antebraço, pulso, costela"
                  minLength={2}
                  maxLength={80}
                  required
                />
              </label>

              <label className="campo">
                <span>
                  Tamanho estimado (cm)
                  <span className="campo-dica">Ex: 7.5 ou 15</span>
                </span>
                <input
                  name="tamanho"
                  type="number"
                  min="0.1"
                  step="0.5"
                  value={formulario.tamanho}
                  onChange={(evento) => mudar("tamanho", evento.target.value)}
                  placeholder="Ex.: 10"
                  required
                />
              </label>
            </div>

            {erro ? <p className="mensagem-erro" role="alert">{erro}</p> : null}

            <div style={{ marginTop: "1rem" }}>
              <button type="submit" className="botao" style={{ width: "100%" }} disabled={enviando}>
                {enviando ? "Enviando para o estúdio..." : "Enviar Pedido para Avaliação"}
              </button>
            </div>
          </form>

          {/* Guia & Preview */}
          <aside style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div className="cartao" style={{ background: "var(--cor-superficie-suave)" }}>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>
                Como funciona o processo?
              </h3>
              <ol style={{ paddingLeft: "1.2rem", margin: 0, fontSize: "0.8125rem", color: "var(--cor-texto-medio)", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <li><strong>1. Pedida:</strong> Você envia a ideia e tamanho pretendido.</li>
                <li><strong>2. Desenho Aprovado:</strong> O Vitor desenha o rascunho sob medida e você aprova.</li>
                <li><strong>3. Em Sessões:</strong> Realização das sessões com agulha fina na pele.</li>
                <li><strong>4. Finalizada:</strong> Retoque após a cicatrização completa.</li>
              </ol>
            </div>

            <div className="cartao">
              <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--cor-texto-fraco)", fontWeight: 600 }}>
                Pré-visualização do Registro
              </span>
              <div style={{ marginTop: "0.75rem" }}>
                <h4 style={{ fontSize: "1.05rem", color: formulario.ideia ? "var(--cor-texto)" : "var(--cor-texto-fraco)" }}>
                  {formulario.ideia || "Descreva sua ideia..."}
                </h4>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.375rem", fontSize: "0.8125rem", color: "var(--cor-texto-fraco)" }}>
                  <span>{formulario.local_do_corpo || "Local pendente"}</span>
                  <span>·</span>
                  <span>{formulario.tamanho ? `${formulario.tamanho} cm` : "Tamanho pendente"}</span>
                </div>
                <div style={{ marginTop: "0.75rem" }}>
                  <Etiqueta etapa="pedida" />
                </div>
              </div>
            </div>
          </aside>
        </div>
      )}
    </main>
  );
}
