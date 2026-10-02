/* Tela de Boas-Vindas e Escolha de Perfil - Traço Fino */

import AlternadorTema from "../componentes/AlternadorTema";
import Logo from "../componentes/Logo";
import { PERFIS } from "../perfis";
import { ESCURO } from "../tema";

export default function EscolhaPerfil({ aoEscolher, tema, trocarTema }) {
  return (
    <main className="tela">
      {/* Top Header */}
      <header className="cabecalho-secao-topo" style={{ marginBottom: "1.5rem" }}>
        <div className="marca-link">
          <Logo escuro={tema === ESCURO} />
          <span className="marca-status">
            <span className="marca-status-ponto" aria-hidden="true" />
            Estúdio Aberto
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <AlternadorTema tema={tema} trocarTema={trocarTema} />
        </div>
      </header>

      {/* Hero do Estúdio */}
      <section className="hero-estudio">
        <div className="hero-imagem-container">
          <img
            src="/src/assets/images/hero_fine_line_studio_1790901597050.jpg"
            alt="Interior do ateliê Traço Fino, iluminação natural e bancada de desenho"
            className="hero-imagem"
            referrerPolicy="no-referrer"
          />
          <div className="hero-overlay">
            <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.15em", color: "#fed7aa", fontWeight: 600 }}>
              Arte Contemporânea · Single Needle & Botânica
            </span>
            <h1 style={{ color: "#ffffff", fontSize: "2rem", marginTop: "0.25rem", marginBottom: "0.5rem" }}>
              Cada traço com precisão. Cada etapa respeitada.
            </h1>
            <p style={{ color: "rgba(255,255,255,0.85)", fontSize: "0.9375rem", maxWidth: "42rem" }}>
              Acompanhamento transparente das quatro fases da sua tatuagem: da ideia inicial e aprovação do desenho até as sessões de agulha fina e cicatrização final.
            </p>
          </div>
        </div>

        <div className="hero-conteudo">
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: "1rem" }}>
            <div>
              <h2 style={{ fontSize: "1.15rem", marginBottom: "0.25rem" }}>Escolha o perfil para iniciar</h2>
              <p className="subtitulo-secao">
                Selecione abaixo para acessar a interface da cliente ou a gestão do tatuador.
              </p>
            </div>
            <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8125rem", color: "var(--cor-texto-fraco)" }}>
              <span>✓ 4 Etapas Cartilha</span>
              <span>✓ Sem banco / Em memória</span>
              <span>✓ Regras de Sessão</span>
            </div>
          </div>

          <div className="perfis-grid">
            {PERFIS.map((perfil) => (
              <button
                key={perfil.id}
                type="button"
                className="perfil-card"
                onClick={() => aoEscolher(perfil)}
              >
                <div className="perfil-topo">
                  <img
                    src={perfil.avatar}
                    alt={`Foto de ${perfil.nome}`}
                    className="perfil-avatar"
                    referrerPolicy="no-referrer"
                  />
                  <div>
                    <h3 className="perfil-nome">{perfil.nome}</h3>
                    <span className="perfil-tipo-pill">
                      {perfil.tipo} · foco {perfil.aparelho}
                    </span>
                  </div>
                </div>

                <p className="perfil-desc">{perfil.descricao}</p>

                <div className="perfil-rodape">
                  <span>{perfil.tipo === "cliente" ? "Pedir e acompanhar tatuagens" : "Gerenciar agenda e registrar passos"}</span>
                  <span className="perfil-acao-texto">
                    Entrar como {perfil.nome} →
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Vitrine de Arte Macro */}
      <section className="vitrine-estudio">
        <img
          src="/src/assets/images/showcase_botanical_ink_1790901630291.jpg"
          alt="Detalhe de tatuagem botânica com traço fino"
          className="vitrine-foto"
          referrerPolicy="no-referrer"
        />
        <div className="vitrine-texto">
          <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--cor-acento-texto)", fontWeight: 600 }}>
            Compromisso com a Cartilha 4
          </span>
          <h4>Processo cuidadoso em quatro etapas rigorosas</h4>
          <p>
            No Traço Fino, nenhuma sessão começa antes do desenho ter sido formalmente aprovado pela cliente. E nenhum retoque é aceito antes de pelo menos uma sessão concluída. Todo o fluxo é validado pelo serviço para garantir arte com segurança e respeito à pele.
          </p>
        </div>
      </section>
    </main>
  );
}
