/* A lista de perfis.
 *
 * A cartilha diz que, enquanto o login não chega, o front deixa escolher o
 * perfil numa lista, sem senha. Essa lista é fixa aqui, com os dois perfis do
 * sistema: a Bruna, que é cliente, e o Vitor, que é tatuador e dono do Traço
 * Fino. Não existe rota de usuário no back, porque a cartilha não pede uma, e
 * o perfil já é escolhido aqui na tela.
 *
 * O id da Bruna é o mesmo cliente_id que o back exige em qualquer tatuagem
 * dela. O id do Vitor não viaja para o back em lugar nenhum: ele é tatuador, e
 * tatuador não é dono de tatuagem.
 */

export const PERFIS = [
  {
    id: 1,
    nome: "Bruna",
    tipo: "cliente",
    aparelho: "celular",
    descricao: "Primeira tatuagem grande. Descreve a ideia pelo celular.",
  },
  {
    id: 2,
    nome: "Vitor",
    tipo: "tatuador",
    aparelho: "computador",
    descricao: "Tatuador e dono. Organiza a agenda e registra os passos.",
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
