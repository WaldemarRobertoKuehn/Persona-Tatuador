/* O jeito de falar com o back.
 *
 * Este arquivo é o único que sabe a porta do back, e o único que usa fetch. Nenhuma
 * tela chama o back diretamente: a tela chama uma função daqui. Assim, se a porta
 * mudar, muda uma linha só, e o tratamento de erro fica escrito uma vez só.
 *
 * A regra dos três estados da tela é esta: quando a tela carrega, ela começa
 * carregando; quando a chamada volta, ela passa a estar pronta; e quando a
 * chamada falha, ela vira erro com o texto que o back mandou. Isso é feito com
 * useState dentro de cada tela, e o que este arquivo entrega é a promessa de que
 * deu erro já vem com a mensagem pronta.
 */

const URL_DO_BACK = "http://localhost:8000";

/* Monta o caminho com a base e o pedaço que a tela precisa. */
function caminho(pedaco) {
  return `${URL_DO_BACK}${pedaco}`;
}

/* O fetch devolve uma resposta mesmo quando deu erro, então o que precisa ser
 * testado é o campo ok, que vale true só entre 200 e 299. Quando não vale, o
 * motivo da recusa está no campo detail, e ele tem dois formatos. */
async function conferirResposta(resposta) {
  if (!resposta.ok) {
    /* O bloco try/catch existe só para o caso de o back responder um corpo que
     * não é JSON, o que acontece se o servidor estiver no ar mas fora do ar de
     * verdade. Sem ele, o erro do JSON viraria uma exceção sem mensagem útil. */
    let motivo = `A API respondeu ${resposta.status}.`;

    try {
      const corpo = await resposta.json();

      /* O detail das regras do estúdio é texto: é a frase que o serviço escreveu
       * dizendo por que recusou, e ela vai para a tela como está. */
      if (typeof corpo.detail === "string") {
        motivo = corpo.detail;
      } else if (Array.isArray(corpo.detail)) {
        /* O detail de erro de validação é uma lista de objetos, um por campo
         * errado, e cada objeto tem o campo msg. Sem este tratamento, a lista
         * seria transformada em texto e a tela mostraria [object Object].
         *
         * A msg vem escrita em inglês, porque é o Pydantic que a escreve. A
         * frase de fora é a que traduz a situação para quem lê, e o texto técnico
         * fica depois dela, para não esconder informação de quem depura. */
        const tecnico = corpo.detail.map((problema) => problema.msg).join(" ");

        motivo = `O servidor recusou o pedido porque um campo não passou na validação: ${tecnico}`;
      }
    } catch {
      motivo = `A API respondeu ${resposta.status}, sem detalhe.`;
    }

    /* throw new Error interrompe a promise e joga o motivo para o catch da tela,
     * que é quem decide o que mostrar. */
    throw new Error(motivo);
  }

  return resposta.json();
}

/* Lista as tatuagens. Os dois filtros são opcionais, e são os mesmos filtros
 * que a rota do back aceita: etapa e cliente. Sem nenhum, volta tudo. */
export function buscarTatuagens({ etapa, clienteId } = {}) {
  const parametros = new URLSearchParams();

  if (etapa) {
    parametros.set("etapa", etapa);
  }

  if (clienteId) {
    parametros.set("cliente_id", String(clienteId));
  }

  const consulta = parametros.toString();

  return fetch(caminho(`/tatuagens${consulta ? `?${consulta}` : ""}`)).then(
    conferirResposta,
  );
}

/* Mostra uma tatuagem. */
export function buscarTatuagem(tatuagemId) {
  return fetch(caminho(`/tatuagens/${tatuagemId}`)).then(conferirResposta);
}

/* Pede uma tatuagem nova. O POST precisa dos três cabeçalhos: o method diz que
 * está mandando, o Content-Type avisa que o corpo é JSON, e o JSON.stringify
 * transforma o objeto em texto. Sem o Content-Type, o back não entende o corpo. */
export function criarTatuagem(dados) {
  return fetch(caminho("/tatuagens"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  }).then(conferirResposta);
}

/* Lista os passos de uma tatuagem, que é o histórico que a tela da Bruna abre. */
export function buscarPassos(tatuagemId) {
  return fetch(caminho(`/tatuagens/${tatuagemId}/passos`)).then(conferirResposta);
}

/* Registra um passo. O tipo vai exatamente como o back espera, com o til em
 * "sessão": sem ele, o back recusa, porque a regra da cartilha compara o texto
 * inteiro. */
export function registrarPasso(tatuagemId, dados) {
  return fetch(caminho(`/tatuagens/${tatuagemId}/passos`), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  }).then(conferirResposta);
}
