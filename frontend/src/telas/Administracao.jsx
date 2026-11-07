import { URL_DA_API } from "../api";

export default function Administracao() {
  return (
    <main className="tela">
      <h1>Administração</h1>
      <p className="legenda">
        Você está conectado como Administrador. As contas, os grupos e as
        permissões do sistema são gerenciados pela API.
      </p>
      <a
        className="botao botao-neutro"
        href={`${URL_DA_API}/docs`}
        target="_blank"
        rel="noreferrer"
      >
        Abrir administração da API
      </a>
    </main>
  );
}