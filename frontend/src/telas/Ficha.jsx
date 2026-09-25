/* Tela 4 da cartilha: A ficha, do Vitor, no computador.
 *
 * A ficha é o formulário que registra um passo numa tatuagem. Ela tem duas metades:
 * à esquerda, de quem é a tatuagem e o que já foi feito nela; à direita, o
 * formulário. No celular as duas metades empilham, na ordem em que se lê: primeiro
 * o que é a tattoo, depois o que fazer com ela.
 *
 * Esta tela é onde a regra da cartilha fica visível. O Vitor registra um passo, e
 * duas coisas podem acontecer: o back aceita e a etapa muda, ou o back recusa e
 * devolve o motivo. Os dois casos aparecem na tela, e é por isso que ela recarrega
 * a tattoo depois de registrar: a resposta do POST do passo é o passo, e a etapa é
 * outra coisa, que mora em outro recurso da API.
 *
 * A tela NÃO esconde os passos que a regra recusa. O seletor traz os três tipos
 * sempre, porque a regra é do serviço e a tela não vai adivinhar o que é aceito em
 * cada etapa. Se a tela escondesse, o Vitor nunca veria a recusa, e a recusa é
 * parte do que ele precisa entender.
 */

import { useEffect, useState } from "react";

import { buscarPassos, buscarTatuagem, registrarPasso } from "../api";
import Etiqueta from "../componentes/Etiqueta";
import { formatarData } from "../datas";

/* Os três passos que a cartilha fecha. A lista vem para desenhar o seletor, e
 * não para validar: quem valida é o serviço, e a recusa dele é o que o Vitor
 * precisa ver. */
const TIPOS_DE_PASSO = ["desenho aprovado", "sessão", "retoque"];

export default function Ficha({ tatuagem, aoVoltarParaAgenda }) {
  const [etapaAtual, setEtapaAtual] = useState(tatuagem.etapa);
  const [passos, setPassos] = useState([]);
  const [tipo, setTipo] = useState("");
  const [observacao, setObservacao] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [confirmacao, setConfirmacao] = useState("");

  /* Carrega o histórico da tattoo. A busca da tattoo em si não acontece aqui: ela
   * veio pronta da agenda, que já a tinha buscado para mostrar. */
  useEffect(() => {
    buscarPassos(tatuagem.id)
      .then(setPassos)
      .catch((erroRecebido) => setErro(erroRecebido.message));
  }, [tatuagem.id]);

  /* Depois de registrar, duas coisas precisam ser relidas: a etapa, porque ela
   * mudou, e o histórico, porque ganhou um passo. São duas buscas, e não uma,
   * porque a API separa a tattoo do passo em recursos diferentes. */
  function recarregar() {
    buscarTatuagem(tatuagem.id)
      .then((atualizada) => setEtapaAtual(atualizada.etapa))
      .catch(() => {});

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
        /* A confirmação é montada com o passo que o back gravou, e não com o que
         * foi digitado, para o que a tela mostra ser sempre o que ficou gravado. */
        setConfirmacao(
          `${passo.tipo} registrado em ${formatarData(passo.data)}.`,
        );
        setTipo("");
        setObservacao("");
        setEnviando(false);
        recarregar();
      })
      .catch((erroRecebido) => {
        /* A recusa da regra chega aqui como uma string, e ela é mostrada como
         * está. O Vitor precisa do motivo, não de um "deu erro". */
        setErro(erroRecebido.message);
        setEnviando(false);
      });
  }

  return (
    <main className="tela">
      <header className="cabecalho">
        <h1>A ficha</h1>
        <p>
          <button type="button" className="botao-neutro" onClick={aoVoltarParaAgenda}>
            Voltar para a agenda
          </button>
        </p>
      </header>

      <div className="ficha">
        <section className="cartao">
          <div className="cartao-tatuagem">
            <div>
              <h2>{tatuagem.ideia}</h2>
              <p>
                {tatuagem.local_do_corpo} · {tatuagem.tamanho} cm ·{" "}
                {tatuagem.nome_da_cliente}
              </p>
            </div>
            <Etiqueta etapa={etapaAtual} />
          </div>

          {confirmacao ? (
            <div className="confirmacao" role="status">
              <strong>Agora está:</strong>
              <Etiqueta etapa={etapaAtual} />
              <span>{confirmacao}</span>
            </div>
          ) : null}

          <h3>Histórico</h3>
          {passos.length === 0 ? (
            <p className="vazio">Nenhum passo ainda.</p>
          ) : (
            <ol className="lista">
              {passos.map((passo) => (
                <li key={passo.id}>
                  <strong>{passo.tipo}</strong> · {formatarData(passo.data)}
                  {passo.observacao ? <p>{passo.observacao}</p> : null}
                </li>
              ))}
            </ol>
          )}
        </section>

        <form className="cartao" onSubmit={enviar}>
          <h2>Registrar um passo</h2>

          <label className="campo">
            <span>Passo</span>
            <select
              name="tipo"
              value={tipo}
              onChange={(evento) => setTipo(evento.target.value)}
              required
            >
              <option value="">Escolha o passo</option>
              {TIPOS_DE_PASSO.map((nome) => (
                <option key={nome} value={nome}>
                  {nome}
                </option>
              ))}
            </select>
          </label>

          {/* O erro da regra fica embaixo do campo, que é onde o Vitor está olhando
              depois de apertar registrar. */}
          {erro ? (
            <p className="mensagem-erro" role="alert">
              {erro}
            </p>
          ) : null}

          <label className="campo">
            <span>Observação (opcional)</span>
            <textarea
              name="observacao"
              value={observacao}
              onChange={(evento) => setObservacao(evento.target.value)}
              maxLength={500}
              placeholder="O que foi feito neste passo."
            />
          </label>

          <button type="submit" className="botao" disabled={enviando}>
            {enviando ? "Registrando..." : "Registrar passo"}
          </button>
        </form>
      </div>
    </main>
  );
}
