/* Os perfis do sistema, um por papel.
 *
 * O papel é o que o back devolve em /usuarios/eu: "cliente" ou "tatuador". É o
 * back que sabe o que cada pessoa é, e a tela só obedece: por isso o perfil é
 * escolhido pelo papel, e não por um id escrito aqui.
 *
 * O nome que aparece na tela também vem do back, da conta que entrou. Assim o
 * mesmo perfil serve para as duas contas de tatuador do estúdio, o Vitor e o
 * dono, e cada uma aparece com o próprio nome.
 *
 * O id da cliente mora em outro lugar: ele vem da conta, no campo cliente_id,
 * e é ele que a tela usa para filtrar "minhas tatuagens" e para dizer de quem
 * é a tatuagem que está sendo pedida. O id da conta e o id da cliente são
 * coisas diferentes, e o back é quem guarda a ligação entre as duas.
 *
 * O retrato de cada papel é importado como arquivo, e não escrito como caminho
 * de "/src/...". O import é o que faz o Vite copiar a foto para dentro do build
 * com um nome próprio: um caminho escrito à mão funciona em desenvolvimento e
 * some quando o projeto é construído para publicar. O alt do retrato é o nome
 * da pessoa, e a foto é decorativa: quem usa leitor de tela ouve o nome no
 * texto ao lado, e não a foto duas vezes.
 */

import retratoBruna from "./imagens/foto-bruna.jpg";
import retratoVitor from "./imagens/foto-vitor.jpg";

export const PERFIS = {
  cliente: {
    tipo: "cliente",
    aparelho: "celular",
    descricao:
      "Primeira tatuagem grande. Descreve a ideia pelo celular e acompanha cada etapa.",
    retrato: retratoBruna,
  },
  tatuador: {
    tipo: "tatuador",
    aparelho: "computador",
    descricao:
      "Tatuador e dono. Organiza a agenda do estúdio e registra os passos de cada tatuagem.",
    retrato: retratoVitor,
  },
};

/* As quatro telas da cartilha. Cada perfil só enxerga as dele: quem é cliente
 * não tem a agenda, e quem é tatuador não tem o formulário de pedido. */
export const TELAS = {
  cliente: ["pedir", "minhas"],
  tatuador: ["agenda", "ficha"],
};

/* Os textos de cada tela, com o aparelho em que ela precisa ficar impecável. */
export const TEXTOS_DAS_TELAS = {
  pedir: { titulo: "Pedir tatuagem", para: "celular" },
  minhas: { titulo: "Minhas tatuagens", para: "celular" },
  agenda: { titulo: "A agenda", para: "computador" },
  ficha: { titulo: "A ficha", para: "computador" },
};

/* As etapas da cartilha, na ordem em que a tatuagem anda. A lista é usada para
 * desenhar a linha do tempo das etapas e as abas do filtro, e nunca para decidir o
 * que é aceito: essa decisão é do serviço, no back. */
export const ETAPAS = ["pedida", "desenho aprovado", "em sessões", "finalizada"];