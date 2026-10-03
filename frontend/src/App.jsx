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
 * tatuagem é a agenda. Se a escolha ficasse na ficha, a ficha teria de saber o que
 * a agenda escolheu, e as duas telas passariam a se conhecer.
 *
 * A barra fixa do alto é desenhada aqui, e não em cada tela, porque é a única parte
 * da tela que é a mesma nas quatro. Cada tela desenha só o seu conteúdo, e por isso
 * duas telas não podem divergir na barra: uma delas ficaria com o logo, a pessoa e o
 * botão de tema em lugares diferentes.
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
   * aparece. Guardar o perfil inteiro, e não só o id, é para o nome, o tipo e o
   * retrato ficarem disponíveis sem voltar na lista. */
  const [perfil, setPerfil] = useState(null);
  const [tela, setTela] = useState(null);
  const [tatuagemAberta, setTatuagemAberta] = useState(null);

  /* O tema é do App e não de cada tela, porque o botão fica na barra, que é
   * compartilhada. Se cada tela guardasse o seu, o botão de uma tela trocaria
   * só aquela tela, e a pessoa teria um site com dois temas ao mesmo tempo. */
  const { tema, trocarTema } = useTema();

  /* Escolher o perfil também abre a primeira tela dele. Sem isso, a Bruna
   * cairia na tela do Vitor, que não é dela. */
  function escolherPerfil(perfilEscolhido) {
    setPerfil(perfilEscolhido);
    setTela(TELAS[perfilEscolhido.tipo][0]);
  }

  /* Sair do perfil devolve para a lista e limpa a tela e a tatuagem aberta, para o
   * próximo perfil começar do começo dele. */
  function sairDoPerfil() {
    setPerfil(null);
    setTela(null);
    setTatuagemAberta(null);
  }

  /* Abrir a ficha é sempre a mesma coisa: guardar a tatuagem e trocar de tela. A
   * agenda não sabe o nome da tela, e a ficha não sabe de onde a tatuagem veio. */
  function abrirFicha(tatuagem) {
    setTatuagemAberta(tatuagem);
    setTela("ficha");
  }

  /* A escolha de perfil não tem barra: ela é a entrada do sistema, e a barra só
   * faz sentido depois que há alguém usando. */
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
      <div className="barra">
        <div className="barra-conteudo">
          <div className="marca">
            <Logo escuro={tema === ESCURO} />
            <span className="placa">
              <span className="placa-ponto" aria-hidden="true" />
              Estúdio aberto
            </span>
          </div>

          <div className="barra-lado">
            {/* A pessoa que está usando, com o retrato. O retrato aqui é
                decorativo de novo, porque o nome está escrito do lado. */}
            <span className="pessoa">
              <img
                className="pessoa-retrato"
                src={perfil.retrato}
                alt=""
                width="32"
                height="32"
              />
              <span className="pessoa-nome">{perfil.nome}</span>
              <span className="pessoa-tipo">· {perfil.tipo}</span>
            </span>

            <AlternadorTema tema={tema} trocarTema={trocarTema} />
          </div>
        </div>

        {/* As telas do perfil. O aria-current é o que diz ao leitor de tela qual
            é a tela aberta: sem ele, quem navega por teclado ouve quatro botões
            iguais e não sabe onde está. */}
        <ul className="telas">
          {TELAS[perfil.tipo].map((nome) => (
            <li key={nome}>
              <button
                type="button"
                className="tela-link"
                aria-current={nome === tela ? "page" : undefined}
                onClick={() => setTela(nome)}
              >
                {TEXTOS_DAS_TELAS[nome].titulo}
              </button>
            </li>
          ))}

          <li>
            <button type="button" className="tela-link" onClick={sairDoPerfil}>
              Trocar de perfil
            </button>
          </li>
        </ul>
      </div>

      {/* Cada tela é desenhada em um bloco só seu, e só entra quando ela é a
          tela atual. É o que mantém o perfil da Bruna longe da agenda. */}
      {tela === "pedir" ? (
        <PedirTatuagem perfil={perfil} aoConcluir={() => setTela("minhas")} />
      ) : null}

      {tela === "minhas" ? (
        <MinhasTatuagens perfil={perfil} aoAbrirPedido={() => setTela("pedir")} />
      ) : null}

      {tela === "agenda" ? <Agenda aoAbrirFicha={abrirFicha} /> : null}

      {/* A ficha só existe com uma tatuagem aberta. Sem ela, não há em qual
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