/* Tela 4 da cartilha: A ficha, do Vitor, no computador.
 *
 * A ficha é o formulário que registra um passo numa tatuagem. Ela tem duas metades:
 * à esquerda, de quem é a tatuagem e o que já foi feito nela; à direita, o
 * formulário. No celular as duas metades empilham, na ordem em que se lê: primeiro
 * o que é a tatuagem, depois o que fazer com ela.
 *
 * Esta tela é onde a regra da cartilha fica visível. O Vitor registra um passo, e
 * duas coisas podem acontecer: o back aceita e a etapa muda, ou o back recusa e
 * devolve o motivo. Os dois casos aparecem na tela, e é por isso que ela recarrega
 * a tatuagem depois de registrar: a resposta do POST do passo é o passo, e a etapa é
 * outra coisa, que mora em outro recurso da API.
 *
 * A tela NÃO esconde os passos que a regra recusa, e também NÃO escreve a regra
 * aqui. As duas coisas são a mesma escolha: a regra de quais etapas aceitam quais
 * passos é do serviço, e copiá-la para a tela faria duas regras que divergem na
 * primeira correção. O seletor traz os três tipos sempre, e o back é quem recusa e
 * diz por quê.
 */

import { useEffect, useState } from "react";

import { buscarPassos, buscarTatuagem, registrarPasso } from "../api";
import { AvisoCarregando } from "../componentes/Avisos";
import CabecalhoDaTela from "../componentes/CabecalhoDaTela";
import Etiqueta from "../componentes/Etiqueta";
import LinhaDoTempo from "../componentes/LinhaDoTempo";
import ProgressoDasEtapas from "../componentes/ProgressoDasEtapas";
import { formatarData } from "../datas";

/* Os três passos que a cartilha fecha. A lista vem para desenhar o seletor, e
 * não para validar: quem valida é o serviço, e a recusa dele é o que o Vitor
 * precisa ver. */
const TIPOS_DE_PASSO = ["desenho aprovado", "sessão", "retoque"];

export default function Ficha({ tatuagem, aoVoltarParaAgenda }) {
  const [etapaAtual, setEtapaAtual] = useState(tatuagem.etapa);
  const [passos, setPassos] = useState([]);
  /* O que está guardado aqui não é um "carregando", é de qual tatuagem os
   * passos que estão na tela são. O carregando é derivado disso: enquanto não
   * bater com a tatuagem aberta, a tela não sabe o histórico ainda. Assim o
   * estado não é marcado dentro do efeito, e trocar de tatuagem volta a
   * carregar sozinho. */
  const [passosDa, setPassosDa] = useState(null);
  const [tipo, setTipo] = useState("");
  const [observacao, setObservacao] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const [confirmacao, setConfirmacao] = useState("");

  /* Sem esta linha, a lista de passos começa vazia e o histórico escreveria
   * "Nenhum passo ainda" antes de a resposta chegar, que é uma coisa diferente
   * de não ter passo nenhum. */
  const carregando = passosDa !== tatuagem.id;

  /* Carrega o histórico da tatuagem. A busca da tatuagem em si não acontece aqui: ela
   * veio pronta da agenda, que já a tinha buscado para mostrar. */
  /* O vivo é o que impede a resposta velha de chegar depois da nova. Se a tela
   * abrir outra tatuagem com uma busca ainda no ar, o cleanup marca esta como
   * morta e ela para de escrever, em vez de sobrescrever a lista com o histórico
   * da tatuagem anterior. */
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

  /* Depois de registrar, duas coisas precisam ser relidas: a etapa, porque ela
   * mudou, e o histórico, porque ganhou um passo. São duas buscas, e não uma,
   * porque a API separa a tatuagem do passo em recursos diferentes. */
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
      <CabecalhoDaTela
        titulo={`A ficha de ${tatuagem.ideia}`}
        apoio={`Tatuagem ${tatuagem.id}, de ${tatuagem.nome_da_cliente}.`}
        acao={
          <button
            type="button"
            className="botao-neutro"
            onClick={aoVoltarParaAgenda}
          >
            Voltar para a agenda
          </button>
        }
      />

      <div className="ficha">
        {/* A coluna da tatuagem: quem é, em que etapa está e o que já foi feito. */}
        <section className="cartao">
          <div className="topo-do-cartao">
            <div>
              <h2>{tatuagem.ideia}</h2>
              <div className="detalhes">
                <span>
                  local <strong>{tatuagem.local_do_corpo}</strong>
                </span>
                <span className="separador" aria-hidden="true">
                  ·
                </span>
                <span className="numero">
                  <strong>{tatuagem.tamanho} cm</strong>
                </span>
                <span className="separador" aria-hidden="true">
                  ·
                </span>
                <span>
                  cliente <strong>{tatuagem.nome_da_cliente}</strong>
                </span>
              </div>
            </div>

            <Etiqueta etapa={etapaAtual} />
          </div>

          <ProgressoDasEtapas etapa={etapaAtual} />

          {confirmacao ? (
            <div className="confirmacao" role="status">
              <strong>Agora está:</strong>
              <Etiqueta etapa={etapaAtual} />
              <span>{confirmacao}</span>
            </div>
          ) : null}

          <h3>Histórico</h3>

          {carregando ? (
            <AvisoCarregando oQue="o histórico" />
          ) : passos.length === 0 ? (
            <p className="vazio">Nenhum passo ainda.</p>
          ) : (
            <LinhaDoTempo passos={passos} />
          )}
        </section>

        {/* A coluna do formulário. */}
        <section className="cartao">
          <h2>Registrar um passo</h2>
          <p className="legenda legenda-folgada">
            A regra do estúdio é do servidor: se a etapa atual não aceitar o passo,
            o motivo da recusa aparece embaixo do campo.
          </p>

          <form onSubmit={enviar}>
            <label className="campo">
              <span>Passo</span>
              <select
                name="tipo"
                value={tipo}
                onChange={(evento) => {
                  setTipo(evento.target.value);
                  /* Limpar o erro ao escolher outro passo é o que faz a recusa
                   * sumir quando ela deixou de valer: o erro era daquele passo,
                   * e a escolha mudou. */
                  setErro("");
                }}
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

            <label className="campo-com-dica">
              {/* O campo com dica usa uma tag própria porque o rótulo dele tem duas
                  partes: o nome do campo e o contador de caracteres, que é
                  --cor-texto-fraco e menor, porque ajuda e não é o pedido. */}
              <span className="campo-rodape">
                Observação (opcional)
                <span className="campo-dica">{observacao.length}/500</span>
              </span>
              <textarea
                name="observacao"
                value={observacao}
                onChange={(evento) => setObservacao(evento.target.value)}
                maxLength={500}
                placeholder="O que foi feito neste passo."
              />
            </label>

            <button type="submit" className="botao botao-largo" disabled={enviando}>
              {enviando ? "Registrando..." : "Registrar passo"}
            </button>
          </form>
        </section>
      </div>
    </main>
  );
}