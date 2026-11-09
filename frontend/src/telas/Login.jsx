/* Tela de entrada do Traço Fino: apresentação do estúdio e login da conta. */

import { useEffect, useState } from "react";

import fotoAtelie from "../imagens/foto-atelie.jpg";
import fotoVitrine from "../imagens/foto-vitrine.jpg";
import AlternadorTema from "../componentes/AlternadorTema";
import CampoSenha from "../componentes/CampoSenha";
import Logo from "../componentes/Logo";
import { ESCURO } from "../tema";

export default function Login({
  aoEntrar,
  aoCadastrar,
  aoSolicitarRedefinicao,
  aoRedefinirSenha,
  aoLimparErro,
  erro,
  entrando,
  cadastrando,
  solicitandoRedefinicao,
  redefinindoSenha,
  tema,
  trocarTema,
}) {
  const tokenInicial = new URLSearchParams(window.location.hash.slice(1)).get(
    "redefinir-senha",
  );
  const [modo, setModo] = useState(tokenInicial ? "redefinir" : "entrar");
  const [tokenRedefinicao, setTokenRedefinicao] = useState(tokenInicial || "");
  const [nome, setNome] = useState("");
  const [identificador, setIdentificador] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmacaoSenha, setConfirmacaoSenha] = useState("");
  const [erroConfirmacao, setErroConfirmacao] = useState("");
  const [mensagemSucesso, setMensagemSucesso] = useState("");
  const ehCadastro = modo === "cadastrar";
  const ehEsqueciSenha = modo === "esqueci";
  const ehRedefinicao = modo === "redefinir";
  const ocupado =
    entrando || cadastrando || solicitandoRedefinicao || redefinindoSenha;

  useEffect(() => {
    if (tokenRedefinicao) {
      window.history.replaceState(
        null,
        "",
        `${window.location.pathname}${window.location.search}`,
      );
    }
  }, [tokenRedefinicao]);

  function trocarModo(novoModo) {
    setModo(novoModo);
    setSenha("");
    setConfirmacaoSenha("");
    setErroConfirmacao("");
    setMensagemSucesso("");
    aoLimparErro();
  }

  async function enviar(evento) {
    evento.preventDefault();

    if (ehCadastro) {
      if (senha !== confirmacaoSenha) {
        setErroConfirmacao("As senhas não coincidem.");
        return;
      }

      const cadastroConcluido = await aoCadastrar(nome, identificador, senha);
      if (cadastroConcluido) {
        trocarModo("entrar");
      }
    } else if (ehEsqueciSenha) {
      const solicitado = await aoSolicitarRedefinicao(identificador);
      if (solicitado) {
        setMensagemSucesso(
          "Se houver uma conta com este email, enviaremos um link para redefinir a senha.",
        );
      }
    } else if (ehRedefinicao) {
      if (senha !== confirmacaoSenha) {
        setErroConfirmacao("As senhas não coincidem.");
        return;
      }

      const redefinida = await aoRedefinirSenha(
        tokenRedefinicao,
        senha,
        confirmacaoSenha,
      );
      if (redefinida) {
        setTokenRedefinicao("");
        setSenha("");
        setConfirmacaoSenha("");
        setMensagemSucesso("Senha alterada. Entre com sua nova senha.");
        setModo("entrar");
      }
    } else {
      aoEntrar(identificador, senha);
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
          : ehEsqueciSenha
            ? "Recuperar acesso"
            : ehRedefinicao
              ? "Criar nova senha"
              : "Entrar no Traço Fino"}
      </h2>
      <p className="legenda">
        {ehCadastro
          ? "Nome, e-mail e senha. Sua conta começa como Cliente."
          : ehEsqueciSenha
            ? "Informe o email da conta para receber um link seguro."
            : ehRedefinicao
              ? "Escolha uma senha nova e confirme antes de salvar."
              : "Use o e-mail ou o usuário e a senha da sua conta."}
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
            <span className="campo-rodape">
              {ehCadastro || ehEsqueciSenha ? "E-mail" : "E-mail ou usuário"}
            </span>
            <input
              type={ehCadastro || ehEsqueciSenha ? "email" : "text"}
              name="identificador"
              value={identificador}
              onChange={(evento) => setIdentificador(evento.target.value)}
              autoComplete={ehCadastro || ehEsqueciSenha ? "email" : "username"}
              maxLength={254}
              required
            />
          </label>
        ) : null}

        {!ehEsqueciSenha ? (
          <CampoSenha
            id="senha"
            name="senha"
            label={ehRedefinicao ? "Nova senha" : "Senha"}
            dica={ehCadastro || ehRedefinicao ? "mínimo 8 caracteres" : null}
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
              label={ehRedefinicao ? "Confirmar nova senha" : "Confirmar senha"}
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

        {mensagemSucesso ? (
          <p className="aviso" role="status">
            {mensagemSucesso}
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={ocupado}>
          {ehCadastro
            ? cadastrando
              ? "Criando conta..."
              : "Criar conta"
            : ehEsqueciSenha
              ? solicitandoRedefinicao
                ? "Enviando..."
                : "Enviar link"
              : ehRedefinicao
                ? redefinindoSenha
                  ? "Salvando..."
                  : "Salvar nova senha"
                : entrando
                  ? "Entrando..."
                  : "Entrar"}
        </button>
      </form>

      {ehCadastro ? (
        <p className="alternar-acesso">
          Já tem uma conta?{" "}
          <button
            type="button"
            className="link-acao"
            onClick={() => trocarModo("entrar")}
            disabled={ocupado}
          >
            Entrar
          </button>
        </p>
      ) : null}

      {modo === "entrar" ? (
        <>
          <p className="alternar-acesso">
            <button
              type="button"
              className="link-acao"
              onClick={() => trocarModo("esqueci")}
              disabled={ocupado}
            >
              Esqueci minha senha
            </button>
          </p>
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
        </>
      ) : null}

      {ehEsqueciSenha || ehRedefinicao ? (
        <p className="alternar-acesso">
          <button
            type="button"
            className="link-acao"
            onClick={() => trocarModo("entrar")}
            disabled={ocupado}
          >
            Voltar para entrar
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

