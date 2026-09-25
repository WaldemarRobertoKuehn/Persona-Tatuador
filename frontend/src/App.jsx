/* O App: quem está usando, em que tela, e de qual tatuagem.
 *
 * O App guarda três coisas, e só três: o perfil escolhido, a tela atual e a
 * tatuagem aberta na ficha. Não há biblioteca de rotas no projeto, porque a
 * cartilha tem quatro telas e elas são uma coisa só: o estado uma da outra. Um
 * useState para a tela resolve, e evita trazer um pacote novo para um problema de
 * quatro telas.
 *
 * Cada perfil só vê as telas dele. Cliente vê pedido e minhas tatuagens; tatuador
 * vê agenda e ficha. A ordem e a lista estão em src/perfis.js, e o App só obedece.
 *
 * A tatuagem aberta mora aqui, e não dentro da ficha, porque quem escolhe a
 * tattoo é a agenda. Se a escolha ficasse na ficha, a ficha teria de saber o que
 * a agenda escolheu, e as duas telas passariam a se conhecer.
 */

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
  /* null significa que ninguém escolheu perfil ainda, e a tela de escolha
   * aparece. Guardar o perfil inteiro, e não só o id, é para o nome e o tipo
   * ficarem disponíveis sem voltar na lista. */
  const [perfil, setPerfil] = useState(null);
  const [tela, setTela] = useState(null);
  const [tatuagemAberta, setTatuagemAberta] = useState(null);

  /* O tema é do App e não de cada tela, porque o botão fica no cabeçalho, que é
   * compartilhado. Se cada tela guardasse o seu, o botão de uma tela trocaria
   * só aquela tela, e a pessoa teria um site com dois temas ao mesmo tempo. */
  const { tema, trocarTema } = useTema();

  /* Escolher o perfil também abre a primeira tela dele. Sem isso, a Bruna
   * cairia na tela do Vitor, que não é dela. */
  function escolherPerfil(perfilEscolhido) {
    setPerfil(perfilEscolhido);
    setTela(TELAS[perfilEscolhido.tipo][0]);
  }

  /* Sair do perfil devolve para a lista e limpa a tela e a tattoo aberta, para o
   * próximo perfil começar do começo dele. */
  function sairDoPerfil() {
    setPerfil(null);
    setTela(null);
    setTatuagemAberta(null);
  }

  /* Abrir a ficha é sempre a mesma coisa: guardar a tattoo e trocar de tela. A
   * agenda não sabe o nome da tela, e a ficha não sabe de onde a tattoo veio. */
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
      <nav className="tela" style={{ paddingBottom: 0 }}>
        <header className="cabecalho">
          <Logo escuro={tema === ESCURO} />
          <div className="cabecalho-lado">
            <p>
              {perfil.nome} · {perfil.tipo}
            </p>
            <AlternadorTema tema={tema} trocarTema={trocarTema} />
          </div>
        </header>

        <ul className="lista" style={{ listStyle: "none", padding: 0 }}>
          {TELAS[perfil.tipo].map((nome) => (
            <li key={nome}>
              <button
                type="button"
                className={nome === tela ? "botao" : "botao-neutro"}
                onClick={() => setTela(nome)}
              >
                {TEXTOS_DAS_TELAS[nome].titulo}
              </button>
            </li>
          ))}

          <li>
            <button type="button" className="botao-neutro" onClick={sairDoPerfil}>
              Trocar de perfil
            </button>
          </li>
        </ul>
      </nav>

      {/* Cada tela é desenhada em um bloco só seu, e só entra quando ela é a
          tela atual. É o que mantém o perfil da Bruna longe da agenda. */}
      {tela === "pedir" ? <PedirTatuagem perfil={perfil} /> : null}
      {tela === "minhas" ? (
        <MinhasTatuagens perfil={perfil} aoAbrirPedido={() => setTela("pedir")} />
      ) : null}
      {tela === "agenda" ? <Agenda aoAbrirFicha={abrirFicha} /> : null}

      {/* A ficha só existe com uma tattoo aberta. Sem ela, não há em qual
          registrar passo, e a tela diz isso em vez de mostrar um formulário
          vazio que não levaria a lugar nenhum. */}
      {tela === "ficha" ? (
        tatuagemAberta ? (
          <Ficha
            tatuagem={tatuagemAberta}
            aoVoltarParaAgenda={() => setTela("agenda")}
          />
        ) : (
          <main className="tela">
            <h1>A ficha</h1>
            <p className="vazio">
              Abra uma tatuagem na agenda para ver a ficha dela.
            </p>
          </main>
        )
      ) : null}
    </div>
  );
}
