/* Os perfis do sistema, um por papel.
 *
 * O papel é o que o back devolve em /usuarios/eu: "cliente" ou "tatuador". É o
 * back que sabe o que cada pessoa é, e a tela só obedece: por isso o perfil é
 * escolhido pelo papel, e não por um id escrito aqui.
 *
 * O nome que aparece na tela também vem do back, da conta que entrou. Assim
 * cada conta usa as telas do papel recebido e mantém sua própria identidade.
 *
 * O id da cliente mora em outro lugar: ele vem da conta, no campo cliente_id,
 * e é ele que a tela usa para filtrar "minhas tatuagens" e para dizer de quem
 * é a tatuagem que está sendo pedida. O id da conta e o id da cliente são
 * coisas diferentes, e o back é quem guarda a ligação entre as duas.
 *
 * A identidade visual usa as iniciais do nome da conta. Não há uma foto padrão
 * compartilhada por papel, então uma persona de demonstração não representa
 * todas as pessoas que entram.
 */

export const PERFIS = {
  cliente: {
    tipo: "cliente",
    rotulo: "Cliente",
    aparelho: "celular",
    descricao:
      "Primeira tatuagem grande. Descreve a ideia pelo celular e acompanha cada etapa.",
  },
  tatuador: {
    tipo: "tatuador",
    rotulo: "Tatuador",
    aparelho: "computador",
    descricao:
      "Organiza a agenda do estúdio e registra os passos de cada tatuagem.",
  },
  administrador: {
    tipo: "administrador",
    rotulo: "Administrador",
    aparelho: "computador",
    descricao: "Administra contas, grupos e permissões do sistema.",
  },
};

/* As quatro telas da cartilha. Cada perfil só enxerga as dele: quem é cliente
 * não tem a agenda, e quem é tatuador não tem o formulário de pedido. */
export const TELAS = {
  cliente: ["pedir", "minhas"],
  tatuador: ["agenda", "ficha"],
  administrador: ["administracao"],
};

/* Os textos de cada tela, com o aparelho em que ela precisa ficar impecável. */
export const TEXTOS_DAS_TELAS = {
  pedir: { titulo: "Pedir tatuagem", para: "celular" },
  minhas: { titulo: "Minhas tatuagens", para: "celular" },
  agenda: { titulo: "A agenda", para: "computador" },
  ficha: { titulo: "A ficha", para: "computador" },
  administracao: { titulo: "Administração", para: "computador" },
};

/* As etapas da cartilha, na ordem em que a tatuagem anda. A lista é usada para
 * desenhar a linha do tempo das etapas e as abas do filtro, e nunca para decidir o
 * que é aceito: essa decisão é do serviço, no back. */
export const ETAPAS = ["pedida", "desenho aprovado", "em sessões", "finalizada"];