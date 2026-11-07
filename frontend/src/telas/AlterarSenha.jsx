import { useState } from "react";

import CampoSenha from "../componentes/CampoSenha";

export default function AlterarSenha({
  aoSalvar,
  aoVoltar,
  aoLimparErro,
  erro,
  salvando,
}) {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacaoSenha, setConfirmacaoSenha] = useState("");
  const [erroConfirmacao, setErroConfirmacao] = useState("");
  const [sucesso, setSucesso] = useState(false);

  async function enviar(evento) {
    evento.preventDefault();
    aoLimparErro();
    setErroConfirmacao("");
    setSucesso(false);

    if (novaSenha !== confirmacaoSenha) {
      setErroConfirmacao("As senhas não coincidem.");
      return;
    }

    const alterada = await aoSalvar(senhaAtual, novaSenha, confirmacaoSenha);
    if (alterada) {
      setSenhaAtual("");
      setNovaSenha("");
      setConfirmacaoSenha("");
      setSucesso(true);
    }
  }

  return (
    <main className="tela">
      <h1>Alterar senha</h1>
      <p className="legenda">Confirme sua senha atual antes de salvar a nova.</p>

      <form className="cartao" onSubmit={enviar}>
        <CampoSenha
          id="senha-atual"
          name="senhaAtual"
          label="Senha atual"
          autoComplete="current-password"
          minLength={1}
          maxLength={128}
          value={senhaAtual}
          onChange={setSenhaAtual}
        />

        <CampoSenha
          id="nova-senha"
          name="novaSenha"
          label="Nova senha"
          dica="mínimo 8 caracteres"
          autoComplete="new-password"
          minLength={8}
          maxLength={128}
          value={novaSenha}
          onChange={setNovaSenha}
        />

        <CampoSenha
          id="confirmacao-nova-senha"
          name="confirmacaoSenha"
          label="Confirmar nova senha"
          autoComplete="new-password"
          minLength={8}
          maxLength={128}
          value={confirmacaoSenha}
          onChange={setConfirmacaoSenha}
          invalido={Boolean(erroConfirmacao)}
          descricaoId="erro-confirmacao-senha"
        />

        {erroConfirmacao ? (
          <p className="aviso aviso-erro" id="erro-confirmacao-senha" role="alert">
            {erroConfirmacao}
          </p>
        ) : null}
        {erro ? (
          <p className="aviso aviso-erro" role="alert">
            {erro}
          </p>
        ) : null}
        {sucesso ? (
          <p className="aviso" role="status">
            Senha alterada com sucesso.
          </p>
        ) : null}

        <button className="botao botao-largo" type="submit" disabled={salvando}>
          {salvando ? "Salvando..." : "Salvar nova senha"}
        </button>
      </form>

      <button className="botao-neutro" type="button" onClick={aoVoltar}>
        Voltar
      </button>
    </main>
  );
}