/* A linha do tempo da tatuagem, com os quatro pontos da cartilha.
 *
 * A regra da cartilha é que a tatuagem nasce pedida e só anda para desenho
 * aprovado, sessão e retoque, nessa ordem. Este componente é essa regra desenhada:
 * um ponto por etapa, e o que já passou fica cheio, o que é o agora fica no
 * acento. Ele não decide o que é aceito — quem decide é o serviço, no back — ele
 * só mostra em que etapa a tatuagem está.
 *
 * A régua do meio é feita com dois elementos posicionados por cima da linha dos
 * pontos, e não com um traço deitado atrás deles: o pedaço andado é o --cor-acento
 * e ele precisa terminar exatamente no centro do ponto atual, que é uma conta de
 * posição, não de cor.
 */

const ORDEM_DAS_ETAPAS = [
  "pedida",
  "desenho aprovado",
  "em sessões",
  "finalizada",
];

/* O nome curto que aparece embaixo do ponto. A etapa inteira é o nome que o back
 * devolve, e "desenho aprovado" embaixo de um ponto de 24 pixels não caberia sem
 * quebrar a linha. O nome da etapa por inteiro continua aparecendo na etiqueta,
 * que é onde ele é informação. */
const NOMES_CURTOS = {
  pedida: "Pedida",
  "desenho aprovado": "Desenho",
  "em sessões": "Sessões",
  finalizada: "Finalizada",
};

export default function ProgressoDasEtapas({ etapa }) {
  /* O índice da etapa atual na ordem da cartilha. Quando a etapa é um texto que o
   * back ainda não conhece, o indexOf devolve -1, e o que aparece é a linha toda
   * vazia: é melhor uma régua sem nada andado do que um ponto aceso no lugar
   * errado. */
  const posicao = ORDEM_DAS_ETAPAS.indexOf(etapa);
  const chegou = posicao >= 0;

  /* Quanto da régua está andado, em porcentagem. São três intervalos entre quatro
   * pontos, e é por isso que o denominador é o tamanho da lista menos um: se fosse
   * o tamanho da lista, o último ponto cairia fora da régua. */
  const andado = chegou ? (posicao / (ORDEM_DAS_ETAPAS.length - 1)) * 100 : 0;

  /* Onde a régua começa e termina, em porcentagem da largura do componente. Os
   * quatro pontos são colunas iguais, então o centro do primeiro fica a um quarto
   * de coluna da borda: 12,5% de cada lado. A régua nasce nesse ponto e não na
   * borda, senão ela começaria sobrando para fora do primeiro marcador. */
  const INICIO_DA_REGUA = 12.5;

  /* A trilha entre o primeiro e o último ponto é três quartos da largura, que é
   * 100 menos os 12,5% de cada ponta. A porcentagem do passo vale para essa
   * trilha, e não para a largura toda: sem esta conta, o pedaço andado passaria
   * do ponto quando a tatuagem chegasse à última etapa. */
  const LARGURA_DA_TRILHA = 75;

  return (
    <div
      className="progresso"
      role="img"
      aria-label={`Etapa atual: ${etapa}. Etapa ${chegou ? posicao + 1 : "?"} de ${ORDEM_DAS_ETAPAS.length}.`}
    >
      {/* A régua parada: ela vai de ponta a ponta da trilha e é a cor da borda. */}
      <span
        className="progresso-regua"
        style={{ left: `${INICIO_DA_REGUA}%`, right: `${INICIO_DA_REGUA}%`, top: "0.6875rem" }}
        aria-hidden="true"
      />

      {/* O pedaço andado: ele vai do primeiro ponto até o atual, e é o acento. */}
      {chegou ? (
        <span
          className="progresso-andado"
          style={{
            left: `${INICIO_DA_REGUA}%`,
            width: `${(andado / 100) * LARGURA_DA_TRILHA}%`,
            top: "0.6875rem",
          }}
          aria-hidden="true"
        />
      ) : null}

      {ORDEM_DAS_ETAPAS.map((nome, indice) => {
        /* "já passou" é menor que a atual, e "é a atual" é igual. São as duas
         * únicas coisas que a régua sabe, e elas vêm da posição, não do nome. */
        const passou = chegou && indice < posicao;
        const atual = chegou && indice === posicao;

        return (
          <div
            key={nome}
            className={`progresso-passo ${
              passou ? "progresso-passo-espera" : ""
            } ${atual ? "progresso-passo-atual" : ""}`}
          >
            {/* O número do passo, e o visto quando ele já passou. O visto é
                texto e não imagem, e por isso o leitor de tela lê o número: o
                aria-hidden aqui é só para o desenho não ser lido duas vezes. */}
            <span className="progresso-marcador" aria-hidden="true">
              {passou ? "✓" : indice + 1}
            </span>
            <span className="progresso-nome">{NOMES_CURTOS[nome]}</span>
          </div>
        );
      })}
    </div>
  );
}