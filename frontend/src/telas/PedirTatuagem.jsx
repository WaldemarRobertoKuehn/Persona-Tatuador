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
 */

import { useState } from "react";

import { criarTatuagem } from "../api";

export default function PedirTatuagem({ perfil }) {
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

  return (
    <main className="tela">
      <header className="cabecalho">
        <h1>Pedir tatuagem</h1>
        <p>{perfil.nome}</p>
      </header>

      <form className="cartao" onSubmit={enviar}>
        {/* Os limites minLength, maxLength e min repetem os limites do esquema
          * do back, e a diferença é que quem valida é o próprio navegador, que
          * impede o envio e escreve o aviso no idioma de quem está usando. É a
          * forma mais barata de não deixar o 422 chegar na tela. */}
        <label className="campo">
          <span>Sua ideia</span>
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

        <label className="campo">
          <span>Onde no corpo</span>
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
          <span>Tamanho em centímetros</span>
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

        <button type="submit" className="botao" disabled={enviando}>
          {enviando ? "Enviando..." : "Enviar pedido"}
        </button>

        {erro ? <p className="mensagem-erro">{erro}</p> : null}
        {foiGravado && !erro ? (
          <p className="mensagem-erro" style={{ color: "var(--cor-texto)" }}>
            Pedido registrado. A tatuagem já está como pedida.
          </p>
        ) : null}
      </form>
    </main>
  );
}
