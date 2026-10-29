/* Tela de entrada do Traço Fino: apresentação do estúdio e login da conta. */

import { useState } from "react";

import fotoAtelie from "../imagens/foto-atelie.jpg";
import fotoVitrine from "../imagens/foto-vitrine.jpg";
import AlternadorTema from "../componentes/AlternadorTema";
import Logo from "../componentes/Logo";
import { ESCURO } from "../tema";

export default function Login({
  aoEntrar,
  aoCadastrar,
  aoLimparErro,
  erro,
  entrando,
  cadastrando,
  tema,
  trocarTema,
}) {
  const [modo, setModo] = useState("entrar");
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const ehCadastro = modo === "cadastrar";
  const ocupado = entrando || cadastrando;

  function trocarModo(novoModo) {
    setModo(novoModo);
    setSenha("");
    aoLimparErro();
  }

  function enviar(evento) {
    evento.preventDefault();

    if (ehCadastro) {
      aoCadastrar(nome, email, senha);
    } else {
      aoEntrar(email, senha);
    }
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

      <h2>{ehCadastro ? "Criar sua conta" : "Entrar no Traço Fino"}</h2>
      <p className="legenda">
        {ehCadastro
          ? "Nome, e-mail e senha. Sua conta começa como Cliente."
          : "Use o e-mail e a senha da sua conta."}
      </p>

      <form className="cartao" onSubmit={enviar}>
        {ehCadastro ? (
          <label className="campo">
            <span className="campo-rodape">Nome</span>
            <input
              type="text"
              name="nome"
              value={nome}
              onChange={(evento) => setNome(evento.target.value)}
              autoComplete="name"
              minLength={2}
              maxLength={100}
              required
            />
          </label>
        ) : null}

        <label className="campo">
          <span className="campo-rodape">E-mail</span>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(evento) => setEmail(evento.target.value)}
            autoComplete={ehCadastro ? "email" : "username"}
            maxLength={254}
            required
          />
        </label>

        <label className="campo">
          <span className="campo-rodape">
            Senha
            {ehCadastro ? <span className="campo-dica"> mínimo 8 caracteres</span> : null}
          </span>
          <input
            type="password"
            name="senha"
            value={senha}
            onChange={(evento) => setSenha(evento.target.value)}
            autoComplete={ehCadastro ? "new-password" : "current-password"}
            minLength={ehCadastro ? 8 : 1}
            maxLength={128}
            required
          />
        </label>

        {erro ? (
          <p className="aviso aviso-erro" role="alert">
            {erro}
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={ocupado}>
          {ehCadastro
            ? cadastrando
              ? "Criando conta..."
              : "Criar conta"
            : entrando
              ? "Entrando..."
              : "Entrar"}
        </button>
      </form>

      <p className="alternar-acesso">
        {ehCadastro ? "Já tem uma conta?" : "Ainda não tem conta?"}{" "}
        <button
          type="button"
          className="link-acao"
          onClick={() => trocarModo(ehCadastro ? "entrar" : "cadastrar")}
          disabled={ocupado}
        >
          {ehCadastro ? "Entrar" : "Criar conta"}
        </button>
      </p>

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
