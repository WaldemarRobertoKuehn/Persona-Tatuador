/* O jeito de falar com o back.
 *
 * Este arquivo é o único que usa fetch. Nenhuma tela chama o back diretamente:
 * a tela chama uma função daqui. O endereço da API vem do ambiente do Vite, e o
 * tratamento de erro e o cabeçalho do token ficam escritos uma vez só.
 *
 * A regra dos três estados da tela é esta: quando a tela carrega, ela começa
 * carregando; quando a chamada volta, ela passa a estar pronta; e quando a
 * chamada falha, ela vira erro com o texto que o back mandou. Isso é feito com
 * useState dentro de cada tela, e o que este arquivo entrega é a promessa de que
 * deu erro já vem com a mensagem pronta.
 */

export const URL_DA_API = (import.meta.env.VITE_URL_DA_API || "/api").replace(/\/$/, "");
const CHAVE_TOKEN = "traco-fino-token";

let tokenAcesso = null;

/* Monta o caminho com a base e o pedaço que a tela precisa. */
function caminho(pedaco) {
  return `${URL_DA_API}${pedaco}`;
}

function opcoesAutenticadas(opcoes = {}) {
  return {
    ...opcoes,
    headers: {
      ...(tokenAcesso ? { Authorization: `Bearer ${tokenAcesso}` } : {}),
      ...opcoes.headers,
    },
  };
}

export function tokenSalvo() {
  tokenAcesso = sessionStorage.getItem(CHAVE_TOKEN);
  return tokenAcesso;
}

export function guardarToken(token) {
  tokenAcesso = token;
  sessionStorage.setItem(CHAVE_TOKEN, token);
}

export function limparToken() {
  tokenAcesso = null;
  sessionStorage.removeItem(CHAVE_TOKEN);
}

export function milissegundosAteExpirar(token = tokenAcesso) {
  const parteConteudo = token.split(".")[1];
  const base64 = parteConteudo.replace(/-/g, "+").replace(/_/g, "/");
  const preenchido = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  const conteudo = JSON.parse(atob(preenchido));
  const expiracao = Number(conteudo.exp);

  if (!Number.isFinite(expiracao)) {
    throw new Error("O token não contém uma data de expiração válida.");
  }

  return Math.max(0, expiracao * 1000 - Date.now());
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

  /* O DELETE bem-sucedido responde 204, sem corpo. Chamar .json() aqui viraria
   * um erro de JSON em uma resposta que deu certo. */
  if (resposta.status === 204) {
    return null;
  }

  return resposta.json();
}

export function autenticar(identificador, senha) {
  return fetch(caminho("/autenticacao/login"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identificador, senha }),
  })
    .then(conferirResposta)
    .then((dados) => {
      guardarToken(dados.access_token);
      return dados;
    });
}

export function solicitarRedefinicaoSenha(email) {
  return fetch(caminho("/autenticacao/esqueci-senha"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  }).then(conferirResposta);
}

export function redefinirSenha({ token, senha, confirmacaoSenha }) {
  return fetch(caminho("/autenticacao/redefinir-senha"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      token,
      senha,
      confirmacao_senha: confirmacaoSenha,
    }),
  }).then(conferirResposta);
}

export function alterarSenha({ senhaAtual, novaSenha, confirmacaoSenha }) {
  return fetch(
    caminho("/autenticacao/alterar-senha"),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        senha_atual: senhaAtual,
        nova_senha: novaSenha,
        confirmacao_senha: confirmacaoSenha,
      }),
    }),
  ).then(conferirResposta);
}

export function cadastrarUsuario({ nome, email, usuario, senha }) {
  return fetch(caminho("/usuarios"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, email, usuario, senha }),
  }).then(conferirResposta);
}

export function buscarUsuarioAtual(token = tokenAcesso) {
  return fetch(
    caminho("/usuarios/eu"),
    opcoesAutenticadas({
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    }),
  ).then(conferirResposta);
}

/* Define ou troca o usuário curto da conta logada. A conta antiga, que nasceu
 * sem usuário, usa esta rota para escolher um. */
export function definirUsuario(usuario) {
  return fetch(
    caminho("/usuarios/eu/usuario"),
    opcoesAutenticadas({
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario }),
    }),
  ).then(conferirResposta);
}

/* Lista as contas do grupo tatuador para a tela de administração. */
export function buscarTatuadores() {
  return fetch(
    caminho("/usuarios/tatuadores"),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Cria uma conta no grupo tatuador. A rota é administrativa e fixa o papel no
 * back: a tela não pode pedir outro grupo. */
export function cadastrarTatuador({ nome, email, usuario, senha }) {
  return fetch(
    caminho("/usuarios/tatuadores"),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, email, usuario, senha }),
    }),
  ).then(conferirResposta);
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

  return fetch(
    caminho(`/tatuagens${consulta ? `?${consulta}` : ""}`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Mostra uma tatuagem. */
export function buscarTatuagem(tatuagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Pede uma tatuagem nova. O POST precisa dos três cabeçalhos: o method diz que
 * está mandando, o Content-Type avisa que o corpo é JSON, e o JSON.stringify
 * transforma o objeto em texto. Sem o Content-Type, o back não entende o corpo. */
export function criarTatuagem(dados) {
  return fetch(
    caminho("/tatuagens"),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }),
  ).then(conferirResposta);
}

/* Troca o tatuador responsável pela agenda de uma tatuagem. */
export function atribuirTatuador(tatuagemId, tatuadorId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/tatuador`),
    opcoesAutenticadas({
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tatuador_id: tatuadorId }),
    }),
  ).then(conferirResposta);
}

/* Lista os passos de uma tatuagem, que é o histórico que a tela da Bruna abre. */
export function buscarPassos(tatuagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/passos`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Solicita um rascunho de resumo sem enviar dados pessoais nem gravar a resposta. */
export function gerarResumoIA(tatuagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/resumo-ia`),
    opcoesAutenticadas({ method: "POST" }),
  ).then(conferirResposta);
}

/* Gera uma simulação fictícia em quatro etapas, sem gravar dados do estúdio. */
export function simularAtendimentoStudio(situacao) {
  return fetch(
    caminho("/simulacoes/studio"),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ situacao }),
    }),
  ).then(conferirResposta);
}

/* Registra um passo. O tipo vai exatamente como o back espera, com o til em
 * "sessão": sem ele, o back recusa, porque a regra da cartilha compara o texto
 * inteiro. */
export function registrarPasso(tatuagemId, dados) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/passos`),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }),
  ).then(conferirResposta);
}

/* Lista os metadados das imagens. Os bytes não vêm nesta resposta. */
export function buscarImagens(tatuagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Envia o arquivo cru no corpo da requisição. O nome e o tipo vão na query
 * string; o Content-Type é o do próprio arquivo, e não JSON. */
export function enviarImagem(tatuagemId, { arquivo, tipo, nome }) {
  const parametros = new URLSearchParams();
  parametros.set("tipo", tipo);
  parametros.set("nome", nome || arquivo.name || "imagem");

  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens?${parametros.toString()}`),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": arquivo.type },
      body: arquivo,
    }),
  ).then(conferirResposta);
}

/* Busca os bytes da imagem. O <img> não manda o token, então a tela precisa
 * buscar o arquivo por aqui e criar um object URL com o blob recebido. */
export function buscarConteudoImagem(tatuagemId, imagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens/${imagemId}`),
    opcoesAutenticadas(),
  ).then(async (resposta) => {
    if (!resposta.ok) {
      let motivo = `A API respondeu ${resposta.status}.`;

      try {
        const corpo = await resposta.json();
        if (typeof corpo.detail === "string") {
          motivo = corpo.detail;
        }
      } catch {
        motivo = `A API respondeu ${resposta.status}, sem detalhe.`;
      }

      throw new Error(motivo);
    }

    return resposta.blob();
  });
}

export function aprovarImagem(tatuagemId, imagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens/${imagemId}/aprovacao`),
    opcoesAutenticadas({ method: "POST" }),
  ).then(conferirResposta);
}

export function recusarImagem(tatuagemId, imagemId, motivo) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens/${imagemId}/recusa`),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ motivo }),
    }),
  ).then(conferirResposta);
}

export function removerImagem(tatuagemId, imagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/imagens/${imagemId}`),
    opcoesAutenticadas({ method: "DELETE" }),
  ).then(conferirResposta);
}

/* Lista a agenda da tatuagem, inclusive os agendamentos cancelados. */
export function buscarAgendamentos(tatuagemId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/agendamentos`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

/* Pede os horários de um dia. A data vai no formato ISO, "2026-11-07". */
export function buscarDisponibilidade(tatuagemId, data) {
  const parametros = new URLSearchParams({ data });

  return fetch(
    caminho(`/tatuagens/${tatuagemId}/agendamentos/disponibilidade?${parametros.toString()}`),
    opcoesAutenticadas(),
  ).then(conferirResposta);
}

export function criarAgendamento(tatuagemId, dados) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/agendamentos`),
    opcoesAutenticadas({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }),
  ).then(conferirResposta);
}

export function cancelarAgendamento(tatuagemId, agendamentoId) {
  return fetch(
    caminho(`/tatuagens/${tatuagemId}/agendamentos/${agendamentoId}`),
    opcoesAutenticadas({ method: "DELETE" }),
  ).then(conferirResposta);
}
