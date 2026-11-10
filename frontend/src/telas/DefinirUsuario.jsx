import { useState } from "react";

export default function DefinirUsuario({
  usuarioAtual,
  aoSalvar,
  aoVoltar,
  aoLimparErro,
  erro,
  salvando,
}) {
  const [usuario, setUsuario] = useState(usuarioAtual ?? "");
  const [sucesso, setSucesso] = useState(false);

  async function enviar(evento) {
    evento.preventDefault();
    aoLimparErro();
    setSucesso(false);

    const definido = await aoSalvar(usuario);
    if (definido) {
      setSucesso(true);
    }
  }

  return (
    <main className="tela">
      <h1>{usuarioAtual ? "Usuário" : "Definir usuário"}</h1>
      <p className="legenda">
        {usuarioAtual
          ? "Este é o nome curto que você usa para entrar, além do e-mail."
          : "Escolha o nome curto que você vai usar para entrar, além do e-mail."}
      </p>

      <form className="cartao" onSubmit={enviar}>
        <label className="campo">
          <span className="campo-rodape">
            Usuário
            <span className="campo-dica">
              3 a 50 caracteres: letras, números, ponto, hífen ou sublinhado
            </span>
          </span>
          <input
            type="text"
            name="usuario"
            value={usuario}
            onChange={(evento) => setUsuario(evento.target.value.toLowerCase())}
            autoComplete="username"
            minLength={3}
            maxLength={50}
            pattern="[A-Za-z0-9][A-Za-z0-9._-]{2,49}"
            title="Use de 3 a 50 caracteres: letras, números, ponto, hífen ou sublinhado."
            required
          />
        </label>

        {erro ? (
          <p className="aviso aviso-erro" role="alert">
            {erro}
          </p>
        ) : null}
        {sucesso ? (
          <p className="aviso" role="status">
            Usuário definido com sucesso.
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={salvando}>
          {salvando ? "Salvando..." : "Salvar usuário"}
        </button>
      </form>

      <button className="botao-neutro" type="button" onClick={aoVoltar}>
        Voltar
      </button>
    </main>
  );
}
