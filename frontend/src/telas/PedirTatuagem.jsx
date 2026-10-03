/* Tela 1 da cartilha: Pedir tatuagem, da Bruna, no celular.
 *
 * É o formulário em que a Bruna descreve a ideia. Ela não conhece o vocabulário
 * do estúdio, então o formulário fala do jeito dela: ideia, local do corpo e
 * tamanho. Os três campos são exatamente os que o esquema de entrada do back
 * exige, e o 422 que o back devolve aparece embaixo do formulário com o motivo
 * que ele mandou.
 *
 * A tela tem os três estados: enquanto envia, o botão fica desabilitado e mostra
 * que está gravando; se o back recusa, aparece o motivo; se grava, a tela avisa
 * e volta para a lista das tatuagens dela.
 *
 * Ao lado do formulário, no computador, estão as quatro etapas do estúdio e uma
 * prévia do que está sendo enviado. A prévia não é enfeite: ela mostra a etapa
 * que a tatuagem vai ter ao nascer, e esse "pedida" é a única coisa que a tela
 * pode afirmar antes de o back responder.
 */

import { useState } from "react";

import { criarTatuagem } from "../api";
import CabecalhoDaTela from "../componentes/CabecalhoDaTela";
import Etiqueta from "../componentes/Etiqueta";

/* As quatro etapas, na ordem da cartilha. A lista serve para explicar o
 * processo, e não para decidir o que é aceito: essa decisão é do serviço. */
const ETAPAS_EXPLICADAS = [
  { etapa: "pedida", texto: "A ideia chega no estúdio com o tamanho estimado." },
  { etapa: "desenho aprovado", texto: "O desenho é feito sob medida e você aprova." },
  { etapa: "em sessões", texto: "As sessões acontecem com agulha fina na pele." },
  { etapa: "finalizada", texto: "O retoque entra depois da cicatrização." },
];

export default function PedirTatuagem({ perfil, aoConcluir }) {
  /* Os valores dos campos vivem no estado, e cada onChange escreve um campo só.
   * O name do input é o mesmo nome do campo do esquema do back, o que evita
   * traduzir nome de um lado para o outro. */
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

  /* O preventDefault impede o formulário de recarregar a página, que é o
   * comportamento padrão de um form sem JavaScript. */
  function enviar(evento) {
    evento.preventDefault();

    setEnviando(true);
    setErro("");
    setFoiGravado(false);

    /* O tamanho vai como número e não como texto. O campo do esquema do back é
     * numérico, e o Number() deixa o valor do JavaScript com o mesmo tipo do
     * esquema. O que impede o campo vazio de chegar no back é o required e o
     * min do input, explicados mais abaixo. */
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

  /* Depois que o pedido entra, o formulário some e dá lugar ao cartão de
   * sucesso. A tela não volta sozinha para a lista: quem manda é a Bruna, e ela
   * pode querer ver as duas coisas, o pedido que acabou de entrar e a lista. */
  if (foiGravado) {
    return (
      <main className="tela">
        <CabecalhoDaTela
          titulo="Pedir tatuagem"
          apoio={`${perfil.nome}, seu pedido foi registrado.`}
        />

        <section className="cartao sucesso">
          {/* O símbolo é um texto e não um desenho: o styleguide seção 6 proíbe
              ícone no lugar de palavra, e o que importa aqui é a frase. */}
          <span className="sucesso-marca" aria-hidden="true">
            ✓
          </span>

          <h2>Pedido registrado</h2>
          <p className="entrada-apoio">
            Sua ideia já consta na agenda do estúdio como pedida. O Vitor vai
            preparar o desenho e submeter para você aprovar.
          </p>

          <div className="sucesso-acao">
            <button type="button" className="botao" onClick={aoConcluir}>
              Ver minhas tatuagens
            </button>
            <button
              type="button"
              className="botao-neutro"
              onClick={() => setFoiGravado(false)}
            >
              Enviar outro pedido
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="tela">
      <CabecalhoDaTela
        titulo="Pedir tatuagem"
        apoio={`${perfil.nome}, descreva a ideia com as suas palavras.`}
      />

      <div className="ficha">
        <form className="cartao" onSubmit={enviar}>
          {/* Os limites minLength, maxLength e min repetem os limites do esquema
            do back, e a diferença é que quem valida é o próprio navegador, que
            impede o envio e escreve o aviso no idioma de quem está usando. É a
            forma mais barata de não deixar o 422 chegar na tela. */}
          <label className="campo-com-dica">
            <span className="campo-rodape">
              Sua ideia
              <span className="campo-dica">mínimo 10 caracteres</span>
            </span>
            <textarea
              name="ideia"
              value={formulario.ideia}
              onChange={(evento) => mudar("ideia", evento.target.value)}
              placeholder="Descreva com suas palavras o que você quer tatuar."
              minLength={10}
              maxLength={500}
              required
            />
          </label>

          {/* Os dois campos curtos lado a lado só no computador: no celular um
              campo ao lado do outro fica estreito demais para o polegar. */}
          <div className="par">
            <label className="campo">
              <span className="campo-rodape">Onde no corpo</span>
              <input
                name="local_do_corpo"
                value={formulario.local_do_corpo}
                onChange={(evento) => mudar("local_do_corpo", evento.target.value)}
                placeholder="Ex.: antebraço direito"
                minLength={2}
                maxLength={80}
                required
              />
            </label>

            <label className="campo">
              <span className="campo-rodape">
                Tamanho em cm
                <span className="campo-dica">Ex.: 7,5 ou 15</span>
              </span>
              <input
                name="tamanho"
                type="number"
                min="0.1"
                step="0.5"
                value={formulario.tamanho}
                onChange={(evento) => mudar("tamanho", evento.target.value)}
                required
              />
            </label>
          </div>

          {erro ? (
            <p className="mensagem-erro" role="alert">
              {erro}
            </p>
          ) : null}

          <button
            type="submit"
            className="botao botao-largo"
            disabled={enviando}
          >
            {enviando ? "Enviando..." : "Enviar pedido"}
          </button>
        </form>

        {/* A coluna de apoio: como o processo anda, e a prévia do registro. */}
        <section className="cartao">
          <h2>Como o processo anda</h2>
          <ul className="lista-cartoes">
            {ETAPAS_EXPLICADAS.map((item) => (
              <li key={item.etapa}>
                <Etiqueta etapa={item.etapa} />
                <p className="perfil-descricao">{item.texto}</p>
              </li>
            ))}
          </ul>

          {/* A prévia mostra o que vai ser gravado, e a etapa com que ele nasce. */}
          <h3>O que vai ser registrado</h3>
          <p className="perfil-descricao">
            {formulario.ideia || "A ideia que você escrever aqui."}
          </p>
          <p className="detalhes">
            <span>{formulario.local_do_corpo || "local pendente"}</span>
            <span className="separador" aria-hidden="true">
              ·
            </span>
            <span className="numero">
              {formulario.tamanho ? `${formulario.tamanho} cm` : "tamanho pendente"}
            </span>
          </p>
          <Etiqueta etapa="pedida" />
        </section>
      </div>
    </main>
  );
}