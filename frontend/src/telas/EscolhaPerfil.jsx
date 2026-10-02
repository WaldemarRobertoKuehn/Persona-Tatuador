/* A tela de escolha de perfil.
 *
 * Esta tela não é uma das quatro da cartilha, mas a cartilha pede: enquanto o
 * login não chega, o front deixa escolher o perfil numa lista, sem senha. Não há
 * campo de senha aqui, e não há como cadastrar perfil novo. A lista é fixa, e
 * está em src/perfis.js.
 *
 * Escolher o perfil não é autenticação: é escolher com quem a tela vai falar.
 * O id do perfil viaja para o back junto com a requisição, e é isso que faz a
 * tela da Bruna mostrar só as tatuagens dela.
 */

import AlternadorTema from "../componentes/AlternadorTema";
import Logo from "../componentes/Logo";
import { PERFIS } from "../perfis";
import { ESCURO } from "../tema";

export default function EscolhaPerfil({ aoEscolher, tema, trocarTema }) {
  return (
    <main className="tela">
      <header className="cabecalho">
        <Logo escuro={tema === ESCURO} />
        <div className="cabecalho-lado">
          <AlternadorTema tema={tema} trocarTema={trocarTema} />
        </div>
      </header>

      <p className="vazio">
        Escolha quem você é. O sistema ainda não tem senha, então essa escolha é
        só para a tela mostrar o que é seu.
      </p>

      <ul className="lista">
        {PERFIS.map((perfil) => (
          <li key={perfil.id}>
            <button
              type="button"
              className="cartao botao-neutro"
              style={{ width: "100%", textAlign: "left" }}
              onClick={() => aoEscolher(perfil)}
            >
              <strong>{perfil.nome}</strong> · {perfil.tipo}
              <br />
              <small>{perfil.descricao}</small>
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
