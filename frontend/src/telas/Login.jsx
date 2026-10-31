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
  const [confirmacaoSenha, setConfirmacaoSenha] = useState("");
  const [erroConfirmacao, setErroConfirmacao] = useState("");
  const [mostrarAjudaSenha, setMostrarAjudaSenha] = useState(false);
  const ehCadastro = modo === "cadastrar";
  const ocupado = entrando || cadastrando;

  function trocarModo(novoModo) {
    setModo(novoModo);
    setSenha("");
    setConfirmacaoSenha("");
    setErroConfirmacao("");
    setMostrarAjudaSenha(false);
    aoLimparErro();
  }

  function enviar(evento) {
    evento.preventDefault();

    if (ehCadastro) {
      if (senha !== confirmacaoSenha) {
        setErroConfirmacao("As senhas não coincidem.");
        return;
      }

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

        <CampoSenha
          id="senha"
          name="senha"
          label="Senha"
          dica={ehCadastro ? "mínimo 8 caracteres" : null}
          value={senha}
          onChange={(valor) => {
            setSenha(valor);
            setErroConfirmacao("");
          }}
          autoComplete={ehCadastro ? "new-password" : "current-password"}
          minLength={ehCadastro ? 8 : 1}
          maxLength={128}
        />

        {ehCadastro ? (
          <>
            <CampoSenha
              id="confirmacao-senha"
              name="confirmacaoSenha"
              label="Confirmar senha"
              value={confirmacaoSenha}
              onChange={(valor) => {
                setConfirmacaoSenha(valor);
                setErroConfirmacao("");
              }}
              autoComplete="new-password"
              minLength={8}
              maxLength={128}
              invalido={Boolean(erroConfirmacao)}
              descricaoId="erro-confirmacao-senha"
            />
            {erroConfirmacao ? (
              <p
                className="aviso aviso-erro"
                id="erro-confirmacao-senha"
                role="alert"
              >
                {erroConfirmacao}
              </p>
            ) : null}
          </>
        ) : null}

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

      {!ehCadastro ? (
        <>
          <p className="alternar-acesso">
            <button
              type="button"
              className="link-acao"
              aria-expanded={mostrarAjudaSenha}
              aria-controls="ajuda-redefinir-senha"
              onClick={() => setMostrarAjudaSenha(!mostrarAjudaSenha)}
            >
              Esqueceu ou quer redefinir a senha?
            </button>
          </p>
          {mostrarAjudaSenha ? (
            <p className="aviso" id="ajuda-redefinir-senha" role="status">
              Para proteger sua conta, peça ao responsável pelo estúdio para
              redefinir sua senha.
            </p>
          ) : null}
        </>
      ) : null}

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

function CampoSenha({
  id,
  name,
  label,
  dica,
  value,
  onChange,
  autoComplete,
  minLength,
  maxLength,
  invalido = false,
  descricaoId,
}) {
  const [visivel, setVisivel] = useState(false);

  return (
    <div className="campo">
      <label className="campo-rodape" htmlFor={id}>
        {label}
        {dica ? <span className="campo-dica">{dica}</span> : null}
      </label>
      <div className="campo-senha">
        <input
          id={id}
          type={visivel ? "text" : "password"}
          name={name}
          value={value}
          onChange={(evento) => onChange(evento.target.value)}
          autoComplete={autoComplete}
          minLength={minLength}
          maxLength={maxLength}
          aria-invalid={invalido}
          aria-describedby={invalido ? descricaoId : undefined}
          required
        />
        <button
          className="botao-olho"
          type="button"
          aria-label={visivel ? "Ocultar senha" : "Mostrar senha"}
          aria-pressed={visivel}
          onClick={() => setVisivel(!visivel)}
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {visivel ? (
              <>
                <path d="M3 3l18 18" />
                <path d="M10.6 10.6a2 2 0 002.8 2.8" />
                <path d="M9.9 5.2A10.8 10.8 0 0112 5c5 0 8.5 4.5 9.5 7-.4 1-1.3 2.3-2.6 3.5" />
                <path d="M6.2 6.2C3.9 7.6 2.7 9.8 2.5 12c.5 1.2 2.7 5 7.5 6.6a10 10 0 004 .3" />
              </>
            ) : (
              <>
                <path d="M2.5 12S6 5 12 5s9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z" />
                <circle cx="12" cy="12" r="2.5" />
              </>
            )}
          </svg>
        </button>
      </div>
    </div>
  );
}
