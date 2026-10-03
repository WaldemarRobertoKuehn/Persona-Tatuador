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
 *
 * Esta é a primeira tela que a pessoa vê, e por isso ela é a única que tem foto.
 * A foto do ateliê vem antes de qualquer palavra, e o texto fica na superfície
 * abaixo dela, e não escrito por cima: texto sobre foto não tem contraste
 * garantido, e o contraste garantido é o do styleguide seção 1.
 */

import fotoAtelie from "../imagens/foto-atelie.jpg";
import fotoVitrine from "../imagens/foto-vitrine.jpg";
import AlternadorTema from "../componentes/AlternadorTema";
import Logo from "../componentes/Logo";
import { PERFIS } from "../perfis";
import { ESCURO } from "../tema";

export default function EscolhaPerfil({ aoEscolher, tema, trocarTema }) {
  return (
    <main className="tela">
      {/* A placa do estúdio: o logo, a plaquinha e o botão de tema. A troca de
          tema fica nesta tela também, porque é a única tela sem barra, e sem ela
          quem abre o sistema no tema do sistema não teria onde trocar. */}
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

      {/* A foto do ateliê com a frase do estúdio. */}
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
            Você acompanha as quatro fases da sua tatuagem: da ideia e da aprovação
            do desenho até as sessões e o retoque final.
          </p>
        </div>
      </section>

      <h2>Escolha o perfil para entrar</h2>
      <p className="legenda">
        O sistema ainda não tem senha, então a escolha serve só para a tela mostrar o
        que é seu.
      </p>

      <div className="perfis">
        {PERFIS.map((perfil) => (
          <button
            key={perfil.id}
            type="button"
            className="cartao cartao-clicavel"
            onClick={() => aoEscolher(perfil)}
          >
            <div className="perfil-topo">
              <img
                className="perfil-retrato"
                src={perfil.retrato}
                alt=""
                width="48"
                height="48"
              />
              <div>
                <h3>{perfil.nome}</h3>
                <span className="perfil-tipo">
                  {perfil.tipo} · {perfil.aparelho}
                </span>
              </div>
            </div>

            <p className="perfil-descricao">{perfil.descricao}</p>

            <div className="perfil-acao">
              <span>
                {perfil.tipo === "cliente"
                  ? "Pedir e acompanhar tatuagens"
                  : "Organizar a agenda e registrar passos"}
              </span>
              <span className="perfil-acao-forte">Entrar como {perfil.nome}</span>
            </div>
          </button>
        ))}
      </div>

      {/* A vitrine: a foto de uma tatuagem de linha fina e o modo de trabalhar do
          estúdio. Ela existe para a entrada não ser só um formulário, e é a
          mesma frase que a regra da cartilha diz na prática: nenhuma sessão antes
          do desenho aprovado. */}
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
            No Traço Fino nenhuma sessão começa antes de o desenho ter sido aprovado
            pela cliente, e nenhum retoque é aceito antes de existir uma sessão. A
            regra é do estúdio, e quem decide se o passo entra é o servidor, não a
            tela.
          </p>
        </div>
      </section>
    </main>
  );
}