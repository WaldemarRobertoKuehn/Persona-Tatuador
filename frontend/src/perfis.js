/* A lista de perfis e a ordem das telas de cada papel.
 *
 * O login associa os IDs 1 e 2 aos dois papéis existentes: cliente e tatuador.
 * Os IDs também são os cliente_id usados nas tatuagens da Bruna.
 *
 * O id da Bruna é o mesmo cliente_id que o back exige em qualquer tatuagem
 * dela. O id do Vitor não viaja para o back em lugar nenhum: ele é tatuador, e
 * tatuador não é dono de tatuagem.
 *
 * O retrato de cada papel é importado como arquivo, e não escrito como caminho de
 * "/src/...". O import é o que faz o Vite copiar a foto para dentro do build com
 * um nome próprio: um caminho escrito à mão funciona em desenvolvimento e some
 * quando o projeto é construído para publicar. O alt do retrato é o nome da
 * pessoa, e a foto é decorativa: quem usa leitor de tela ouve o nome no texto ao
 * lado, e não a foto duas vezes.
 */

import retratoBruna from "./imagens/foto-bruna.jpg";
import retratoVitor from "./imagens/foto-vitor.jpg";

export const PERFIS = [
  {
    id: 1,
    nome: "Bruna",
    tipo: "cliente",
    aparelho: "celular",
    descricao:
      "Primeira tatuagem grande. Descreve a ideia pelo celular e acompanha cada etapa.",
    retrato: retratoBruna,
  },
  {
    id: 2,
    nome: "Vitor",
    tipo: "tatuador",
    aparelho: "computador",
    descricao:
      "Tatuador e dono. Organiza a agenda do estúdio e registra os passos de cada tatuagem.",
    retrato: retratoVitor,
  },
];

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