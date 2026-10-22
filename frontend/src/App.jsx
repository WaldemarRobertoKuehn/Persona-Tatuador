/* O App: quem está autenticado, em que tela, e de qual tatuagem.
 *
 * O App guarda três coisas, e só três: o perfil autenticado, a tela atual e a
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

import { useEffect, useState } from "react";

import { PERFIS, TELAS, TEXTOS_DAS_TELAS } from "./perfis";
import AlternadorTema from "./componentes/AlternadorTema";
import Logo from "./componentes/Logo";
import { ESCURO, useTema } from "./tema";
import {
  autenticar,
  buscarUsuarioAtual,
  limparToken,
  milissegundosAteExpirar,
  tokenSalvo,
} from "./api";
import Agenda from "./telas/Agenda";
import Ficha from "./telas/Ficha";
import Login from "./telas/Login";
import MinhasTatuagens from "./telas/MinhasTatuagens";
import PedirTatuagem from "./telas/PedirTatuagem";

export default function App() {
  /* O perfil só passa a existir depois de o back validar a conta e seu token. */
  const [perfil, setPerfil] = useState(null);
  const [tela, setTela] = useState(null);
  const [tatuagemAberta, setTatuagemAberta] = useState(null);
  const [estadoAutenticacao, setEstadoAutenticacao] = useState(() =>
    tokenSalvo() ? "verificando" : "desconectado",
  );
  const [entrando, setEntrando] = useState(false);
  const [erroAutenticacao, setErroAutenticacao] = useState("");

  /* O tema é do App e não de cada tela, porque o botão fica na barra, que é
   * compartilhada. Se cada tela guardasse o seu, o botão de uma tela trocaria
   * só aquela tela, e a pessoa teria um site com dois temas ao mesmo tempo. */
  const { tema, trocarTema } = useTema();

  function ativarConta(usuario) {
    /* O perfil vem pelo papel, e não por id: o back é quem sabe o que a pessoa
     * é no estúdio, e a tela só obedece. O nome também vem do back, da conta
     * que entrou, e não deste arquivo. */
    const perfilBase = PERFIS[usuario.papel];

    if (!perfilBase) {
      // NOVO: grupos sem persona visual usam a API administrativa, não as telas React.
      throw new Error(
        usuario.papel === "administrador"
          ? "O grupo Administrador gerencia permissões pela API em /docs; ele não possui telas neste site."
          : "Este grupo não possui telas neste site; use as rotas da API em /docs.",
      );
    }

    /* O clienteId é a ligação com a cliente da cartilha, e ela vem da conta.
     * Sem ele, a tela da cliente não saberia de quem são as tatuagens que ela
     * está olhando, e o filtro "minhas tatuagens" não teria o que enviar. */
    const perfilAutenticado = {
      ...perfilBase,
      nome: usuario.nome,
      clienteId: usuario.cliente_id,
    };

    setPerfil(perfilAutenticado);
    setTela(TELAS[perfilAutenticado.tipo][0]);
    setTatuagemAberta(null);
    setErroAutenticacao("");
    setEstadoAutenticacao("autenticado");
  }

  useEffect(() => {
    const token = tokenSalvo();

    if (!token) {
      return;
    }

    buscarUsuarioAtual(token)
      .then(ativarConta)
      .catch((erroRecebido) => {
        limparToken();
        setErroAutenticacao(
          `Não foi possível restaurar a sessão. Entre novamente. (${erroRecebido.message})`,
        );
        setEstadoAutenticacao("desconectado");
      });
  }, []);

  useEffect(() => {
    if (estadoAutenticacao !== "autenticado") {
      return undefined;
    }

    const token = tokenSalvo();
    const temporizador = setTimeout(() => {
      limparToken();
      setPerfil(null);
      setTela(null);
      setTatuagemAberta(null);
      setErroAutenticacao("Sua sessão expirou. Entre novamente.");
      setEstadoAutenticacao("desconectado");
    }, milissegundosAteExpirar(token));

    return () => clearTimeout(temporizador);
  }, [estadoAutenticacao]);

  async function entrar(email, senha) {
    setEntrando(true);
    setErroAutenticacao("");

    try {
      await autenticar(email, senha);
      const usuario = await buscarUsuarioAtual();
      ativarConta(usuario);
    } catch (erroRecebido) {
      limparToken();
      setErroAutenticacao(erroRecebido.message);
    } finally {
      setEntrando(false);
    }
  }

  function sair() {
    limparToken();
    setPerfil(null);
    setTela(null);
    setTatuagemAberta(null);
    setErroAutenticacao("");
    setEstadoAutenticacao("desconectado");
  }

  /* Abrir a ficha é sempre a mesma coisa: guardar a tatuagem e trocar de tela. A
   * agenda não sabe o nome da tela, e a ficha não sabe de onde a tatuagem veio. */
  function abrirFicha(tatuagem) {
    setTatuagemAberta(tatuagem);
    setTela("ficha");
  }

  if (estadoAutenticacao === "verificando") {
    return (
      <main className="tela">
        <p className="aviso">Verificando sua sessão...</p>
      </main>
    );
  }

  /* A barra só aparece depois que as credenciais e a identidade foram validadas. */
  if (estadoAutenticacao !== "autenticado" || !perfil) {
    return (
      <Login
        aoEntrar={entrar}
        erro={erroAutenticacao}
        entrando={entrando}
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
            <button type="button" className="tela-link" onClick={sair}>
              Sair
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