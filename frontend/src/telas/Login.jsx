/* Tela de entrada do Traço Fino: apresentação do estúdio e login da conta. */

import { useState } from "react";

import fotoAtelie from "../imagens/foto-atelie.jpg";
import fotoVitrine from "../imagens/foto-vitrine.jpg";
import AlternadorTema from "../componentes/AlternadorTema";
import Logo from "../componentes/Logo";
import { ESCURO } from "../tema";

export default function Login({ aoEntrar, erro, entrando, tema, trocarTema }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");

  function enviar(evento) {
    evento.preventDefault();
    aoEntrar(email, senha);
  }

  return (
    <main className="tela">
      <header className="topo-do-cartao">
        <div className="marca">
          <Logo escuro={tema === ESCURO} />
          <span className="placa">
            <span className="placa-ponto" aria-hidden="true" />
            Estúdio aberto
          </span>
        </div>

        <AlternadorTema tema={tema} trocarTema={trocarTema} />
      </header>

      <section className="entrada">
        <img
          className="entrada-imagem"
          src={fotoAtelie}
          alt="Bancada de desenho do ateliê Traço Fino, com luz natural"
          width="1200"
          height="640"
        />

        <div className="entrada-texto">
          <p className="entrada-frase">
            Cada traço com precisão. Cada etapa respeitada.
          </p>
          <p className="entrada-apoio">
            Acompanhe as quatro fases da sua tatuagem: da ideia e da aprovação do
            desenho até as sessões e o retoque final.
          </p>
        </div>
      </section>

      <h2>Entrar no Traço Fino</h2>
      <p className="legenda">Use o e-mail e a senha da sua conta.</p>

      <form className="cartao" onSubmit={enviar}>
        <label className="campo">
          <span className="campo-rodape">E-mail</span>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            autoComplete="username"
            required
          />
        </label>

        <label className="campo">
          <span className="campo-rodape">Senha</span>
          <input
            type="password"
            name="senha"
            value={senha}
            onChange={(evento) => setSenha(evento.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {erro ? (
          <p className="aviso aviso-erro" role="alert">
            {erro}
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={entrando}>
          {entrando ? "Entrando..." : "Entrar"}
        </button>
      </form>

      <section className="vitrine">
        <img
          className="vitrine-foto"
          src={fotoVitrine}
          alt="Detalhe de tatuagem botânica feita com traço fino"
          width="900"
          height="600"
        />

        <div className="vitrine-texto">
          <h3>Quatro etapas, nessa ordem, sempre</h3>
          <p>
            Nenhuma sessão começa antes de o desenho ser aprovado, e nenhum retoque
            é aceito antes de existir uma sessão.
          </p>
        </div>
      </section>
    </main>
  );
}
