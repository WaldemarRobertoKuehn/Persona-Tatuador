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
  aoSolicitarRedefinicao,
  aoRedefinirSenha,
  aoLimparErro,
  erro,
  mensagem,
  entrando,
  cadastrando,
  solicitandoRedefinicao,
  redefinindoSenha,
  tema,
  trocarTema,
}) {
  const tokenInicial = new URLSearchParams(window.location.hash.slice(1)).get("token");
  const [modo, setModo] = useState(tokenInicial ? "redefinir" : "entrar");
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmacaoSenha, setConfirmacaoSenha] = useState("");
  const [erroConfirmacao, setErroConfirmacao] = useState("");
  const [tokenRedefinicao] = useState(tokenInicial);
  const ehCadastro = modo === "cadastrar";
  const ehRecuperacao = modo === "recuperar";
  const ehRedefinicao = modo === "redefinir";
  const ocupado =
    entrando || cadastrando || solicitandoRedefinicao || redefinindoSenha;

  function trocarModo(novoModo) {
    setModo(novoModo);
    setSenha("");
    setConfirmacaoSenha("");
    setErroConfirmacao("");
    aoLimparErro();
  }

  function limparTokenDaUrl() {
    const url = new URL(window.location.href);
    const fragmento = new URLSearchParams(url.hash.slice(1));
    fragmento.delete("token");
    url.hash = fragmento.toString();
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }

  async function enviar(evento) {
    evento.preventDefault();

    if (ehCadastro) {
      if (senha !== confirmacaoSenha) {
        setErroConfirmacao("As senhas não coincidem.");
        return;
      }

      aoCadastrar(nome, email, senha);
    } else if (ehRecuperacao) {
      await aoSolicitarRedefinicao(email);
    } else if (ehRedefinicao) {
      if (senha !== confirmacaoSenha) {
        setErroConfirmacao("As senhas não coincidem.");
        return;
      }

      const redefinida = await aoRedefinirSenha(tokenRedefinicao, senha);
      if (redefinida) {
        limparTokenDaUrl();
        setSenha("");
        setConfirmacaoSenha("");
        setModo("entrar");
      }
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

      <h2>
        {ehCadastro
          ? "Criar sua conta"
          : ehRecuperacao
            ? "Esqueceu a senha?"
            : ehRedefinicao
              ? "Redefinir senha"
              : "Entrar no Traço Fino"}
      </h2>
      <p className="legenda">
        {ehCadastro
          ? "Nome, e-mail e senha. Sua conta começa como Cliente."
          : ehRecuperacao
            ? "Informe o e-mail da conta. O link será enviado ao responsável pelo projeto."
            : ehRedefinicao
              ? "Escolha uma nova senha com pelo menos 8 caracteres."
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

        {!ehRedefinicao ? (
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
        ) : null}

        {!ehRecuperacao ? (
          <CampoSenha
            id="senha"
            name="senha"
            label={ehRedefinicao ? "Nova senha" : "Senha"}
            dica={ehCadastro ? "mínimo 8 caracteres" : null}
            value={senha}
            onChange={(valor) => {
              setSenha(valor);
              setErroConfirmacao("");
            }}
            autoComplete={ehCadastro || ehRedefinicao ? "new-password" : "current-password"}
            minLength={ehCadastro || ehRedefinicao ? 8 : 1}
            maxLength={128}
          />
        ) : null}

        {ehCadastro || ehRedefinicao ? (
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

        {mensagem ? (
          <p className="aviso" role="status">
            {mensagem}
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={ocupado}>
          {ehRecuperacao
            ? solicitandoRedefinicao
              ? "Enviando..."
              : "Enviar link de redefinição"
            : ehRedefinicao
              ? redefinindoSenha
                ? "Salvando..."
                : "Salvar nova senha"
            : ehCadastro
              ? cadastrando
              ? "Criando conta..."
              : "Criar conta"
            : entrando
              ? "Entrando..."
              : "Entrar"}
        </button>
      </form>

      {modo === "entrar" ? (
        <p className="alternar-acesso">
          <button
            type="button"
            className="link-acao"
            onClick={() => trocarModo("recuperar")}
            disabled={ocupado}
          >
            Esqueceu ou quer redefinir a senha?
          </button>
        </p>
      ) : null}

      {ehCadastro ? (
        <p className="alternar-acesso">
          Já tem uma conta?{" "}
          <button
            type="button"
            className="link-acao"
            onClick={() => {
              if (ehRedefinicao) {
                limparTokenDaUrl();
              }
              trocarModo("entrar");
            }}
            disabled={ocupado}
          >
            Entrar
          </button>
        </p>
      ) : null}

      {ehRecuperacao || ehRedefinicao ? (
        <p className="alternar-acesso">
          Lembrou sua senha?{" "}
          <button
            type="button"
            className="link-acao"
            onClick={() => trocarModo("entrar")}
            disabled={ocupado}
          >
            Voltar ao login
          </button>
        </p>
      ) : null}

      {modo === "entrar" ? (
        <p className="alternar-acesso">
          Ainda não tem conta?{" "}
          <button
            type="button"
            className="link-acao"
            onClick={() => trocarModo("cadastrar")}
            disabled={ocupado}
          >
            Criar conta
          </button>
        </p>
      ) : null}

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
