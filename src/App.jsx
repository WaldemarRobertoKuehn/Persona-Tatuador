/* O App: quem está usando, em que tela, e de qual tatuagem. */

import { useState } from "react";

import { TELAS, TEXTOS_DAS_TELAS } from "./perfis";
import AlternadorTema from "./componentes/AlternadorTema";
import Logo from "./componentes/Logo";
import { ESCURO, useTema } from "./tema";
import Agenda from "./telas/Agenda";
import EscolhaPerfil from "./telas/EscolhaPerfil";
import Ficha from "./telas/Ficha";
import MinhasTatuagens from "./telas/MinhasTatuagens";
import PedirTatuagem from "./telas/PedirTatuagem";

export default function App() {
  const [perfil, setPerfil] = useState(null);
  const [tela, setTela] = useState(null);
  const [tatuagemAberta, setTatuagemAberta] = useState(null);

  const { tema, trocarTema } = useTema();

  function escolherPerfil(perfilEscolhido) {
    setPerfil(perfilEscolhido);
    setTela(TELAS[perfilEscolhido.tipo][0]);
  }

  function sairDoPerfil() {
    setPerfil(null);
    setTela(null);
    setTatuagemAberta(null);
  }

  function abrirFicha(tatuagem) {
    setTatuagemAberta(tatuagem);
    setTela("ficha");
  }

  if (!perfil) {
    return (
      <EscolhaPerfil
        aoEscolher={escolherPerfil}
        tema={tema}
        trocarTema={trocarTema}
      />
    );
  }

  return (
    <div>
      {/* Barra de Navegação Superior (Top Bar Contract) */}
      <nav className="barra-navegacao" aria-label="Navegação principal">
        <div className="barra-conteudo">
          {/* Zona 1: Marca do Estúdio */}
          <div className="marca-link">
            <Logo escuro={tema === ESCURO} />
          </div>

          {/* Zona 2: Links de Telas do Perfil */}
          <ul className="nav-links">
            {TELAS[perfil.tipo].map((nome) => (
              <li key={nome}>
                <button
                  type="button"
                  className={`nav-item-btn ${nome === tela ? "ativo" : ""}`}
                  onClick={() => setTela(nome)}
                >
                  {TEXTOS_DAS_TELAS[nome].titulo}
                </button>
              </li>
            ))}
          </ul>

          {/* Zona 3: Usuário Ativo, Trocar e Tema */}
          <div className="nav-acoes">
            <div className="perfil-badge" title={`Conectado como ${perfil.nome}`}>
              <img
                src={perfil.avatar}
                alt=""
                className="perfil-badge-avatar"
                referrerPolicy="no-referrer"
              />
              <span className="perfil-badge-nome">{perfil.nome}</span>
              <span className="perfil-badge-tipo">({perfil.tipo})</span>
            </div>

            <button
              type="button"
              className="botao-neutro botao-sm"
              onClick={sairDoPerfil}
              title="Trocar de perfil"
            >
              Trocar
            </button>

            <AlternadorTema tema={tema} trocarTema={trocarTema} />
          </div>
        </div>
      </nav>

      {/* Renderização da Tela Ativa */}
      {tela === "pedir" ? <PedirTatuagem perfil={perfil} aoConcluir={() => setTela("minhas")} /> : null}
      {tela === "minhas" ? (
        <MinhasTatuagens perfil={perfil} aoAbrirPedido={() => setTela("pedir")} />
      ) : null}
      {tela === "agenda" ? <Agenda aoAbrirFicha={abrirFicha} /> : null}

      {tela === "ficha" ? (
        tatuagemAberta ? (
          <Ficha
            tatuagem={tatuagemAberta}
            aoVoltarParaAgenda={() => setTela("agenda")}
          />
        ) : (
          <main className="tela">
            <div className="cartao vazio">
              <h2>Nenhuma tatuagem selecionada</h2>
              <p style={{ marginTop: "0.5rem" }}>
                Abra uma tatuagem na agenda do estúdio para visualizar e registrar passos.
              </p>
              <button
                type="button"
                className="botao"
                style={{ marginTop: "1rem" }}
                onClick={() => setTela("agenda")}
              >
                Ir para a Agenda
              </button>
            </div>
          </main>
        )
      ) : null}
    </div>
  );
}
