// In-memory data store replicating the FastAPI backend

const clientes = [
  { id: 1, nome: "Bruna" },
  { id: 2, nome: "Camila" },
];

const tatuagens = [
  { id: 1, cliente_id: 1, ideia: "ramo de cerejeira no antebraço", local_do_corpo: "antebraço", tamanho: 12.5, etapa: "finalizada" },
  { id: 2, cliente_id: 1, ideia: "serpente enrolada na canela", local_do_corpo: "canela", tamanho: 20.0, etapa: "em sessões" },
  { id: 3, cliente_id: 2, ideia: "rosa no pulso esquerdo", local_do_corpo: "pulso", tamanho: 7.0, etapa: "desenho aprovado" },
  { id: 4, cliente_id: 1, ideia: "casa no porta-retrato da coxa", local_do_corpo: "coxa", tamanho: 15.0, etapa: "pedida" },
  { id: 5, cliente_id: 2, ideia: "texto 'não desista' no antebraço", local_do_corpo: "antebraço", tamanho: 9.0, etapa: "em sessões" },
  { id: 6, cliente_id: 1, ideia: "folha de figueira na costela", local_do_corpo: "costela", tamanho: 14.0, etapa: "em sessões" },
  { id: 7, cliente_id: 1, ideia: "onda quebrando no tornozelo", local_do_corpo: "tornozelo", tamanho: 6.5, etapa: "desenho aprovado" },
  { id: 8, cliente_id: 2, ideia: "três pontos no ombro, como mapa", local_do_corpo: "ombro", tamanho: 5.0, etapa: "pedida" },
];

const passos = [
  { id: 1, tatuagem_id: 1, tipo: "desenho aprovado", data: "2026-08-03", observacao: "a cliente aprovou o desenho, sem ajuste" },
  { id: 2, tatuagem_id: 1, tipo: "sessão", data: "2026-08-10", observacao: "contorno com linha fina, sem preenchimento" },
  { id: 3, tatuagem_id: 1, tipo: "sessão", data: "2026-08-17", observacao: "preenchimento do fundo e ajuste de traço" },
  { id: 4, tatuagem_id: 1, tipo: "retoque", data: "2026-09-14", observacao: "retoque na ponta de um pétala" },
  { id: 5, tatuagem_id: 2, tipo: "desenho aprovado", data: "2026-09-01", observacao: "aprovado depois de duas mudanças no desenho" },
  { id: 6, tatuagem_id: 2, tipo: "sessão", data: "2026-09-08", observacao: "primeira sessão, só a linha" },
  { id: 7, tatuagem_id: 3, tipo: "desenho aprovado", data: "2026-09-15", observacao: "desenho aprovado, a tatuagem entra na fila das sessões" },
  { id: 8, tatuagem_id: 5, tipo: "desenho aprovado", data: "2026-09-05", observacao: "texto na fonte escolhida pela cliente" },
  { id: 9, tatuagem_id: 5, tipo: "sessão", data: "2026-09-12", observacao: "rascunho da letra" },
  { id: 10, tatuagem_id: 5, tipo: "sessão", data: "2026-09-19", observacao: "letra fechada, aguardando a cicatrização para o retoque" },
  { id: 11, tatuagem_id: 6, tipo: "desenho aprovado", data: "2026-09-08", observacao: "a cliente pediu a folha menor que a primeira versão" },
  { id: 12, tatuagem_id: 6, tipo: "sessão", data: "2026-09-22", observacao: "contorno e primeira parte do sombreado da folha" },
  { id: 13, tatuagem_id: 7, tipo: "desenho aprovado", data: "2026-09-24", observacao: "onda aprovada, entra na fila das sessões" },
];

const REGRAS_DE_PASSO = {
  "desenho aprovado": {
    etapas_aceitas: ["pedida"],
    etapa_nova: "desenho aprovado",
  },
  "sessão": {
    etapas_aceitas: ["desenho aprovado", "em sessões"],
    etapa_nova: "em sessões",
  },
  "retoque": {
    etapas_aceitas: ["em sessões"],
    etapa_nova: "finalizada",
  },
};

function comNomeDaCliente(tatuagem) {
  const cliente = clientes.find((c) => c.id === tatuagem.cliente_id);
  const nome = cliente ? cliente.nome : `cliente ${tatuagem.cliente_id}`;
  return { ...tatuagem, nome_da_cliente: nome };
}

function sendJson(res, statusCode, data) {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(data));
}

function getBody(req) {
  return new Promise((resolve) => {
    if (req.body) return resolve(req.body);
    let data = "";
    req.on("data", (chunk) => {
      data += chunk;
    });
    req.on("end", () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch {
        resolve({});
      }
    });
  });
}

export function apiMiddleware(req, res, next) {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const pathname = url.pathname;

  if (!pathname.startsWith("/tatuagens")) {
    return next();
  }

  // 1. GET /tatuagens/:id/passos
  const matchPassos = pathname.match(/^\/tatuagens\/(\d+)\/passos\/?$/);
  if (matchPassos) {
    const tatuagemId = Number(matchPassos[1]);
    const tatuagem = tatuagens.find((t) => t.id === tatuagemId);
    if (!tatuagem) {
      return sendJson(res, 404, { detail: "Tatuagem não encontrada." });
    }

    if (req.method === "GET") {
      const lista = passos.filter((p) => p.tatuagem_id === tatuagemId);
      return sendJson(res, 200, lista);
    }

    if (req.method === "POST") {
      return getBody(req).then((dados) => {
        const tipo = dados.tipo;
        if (!REGRAS_DE_PASSO[tipo]) {
          return sendJson(res, 422, {
            detail: `'${tipo}' não é um passo deste estúdio. Os passos são: desenho aprovado, sessão e retoque.`,
          });
        }

        const regra = REGRAS_DE_PASSO[tipo];
        if (!regra.etapas_aceitas.includes(tatuagem.etapa)) {
          return sendJson(res, 422, {
            detail: `Não dá para registrar '${tipo}' agora: a tatuagem está '${tatuagem.etapa}', e esse passo só entra em tatuagem que esteja em: ${regra.etapas_aceitas.join(", ")}.`,
          });
        }

        const hoje = new Date().toISOString().split("T")[0];
        const novoPasso = {
          id: passos.length + 1,
          tatuagem_id: tatuagemId,
          tipo: tipo,
          data: hoje,
          observacao: dados.observacao || "",
        };

        passos.push(novoPasso);
        tatuagem.etapa = regra.etapa_nova;
        return sendJson(res, 201, novoPasso);
      });
    }

    return sendJson(res, 405, { detail: "Método não permitido." });
  }

  // 2. GET /tatuagens/:id
  const matchTatuagem = pathname.match(/^\/tatuagens\/(\d+)\/?$/);
  if (matchTatuagem) {
    if (req.method !== "GET") {
      return sendJson(res, 405, { detail: "Método não permitido." });
    }
    const tatuagemId = Number(matchTatuagem[1]);
    const tatuagem = tatuagens.find((t) => t.id === tatuagemId);
    if (!tatuagem) {
      return sendJson(res, 404, { detail: "Tatuagem não encontrada." });
    }
    return sendJson(res, 200, comNomeDaCliente(tatuagem));
  }

  // 3. GET or POST /tatuagens
  if (pathname === "/tatuagens" || pathname === "/tatuagens/") {
    if (req.method === "GET") {
      const etapa = url.searchParams.get("etapa");
      const clienteIdParam = url.searchParams.get("cliente_id");

      let achadas = [...tatuagens];
      if (etapa) {
        achadas = achadas.filter((t) => t.etapa === etapa);
      }
      if (clienteIdParam !== null && clienteIdParam !== "") {
        const cId = Number(clienteIdParam);
        if (!isNaN(cId)) {
          achadas = achadas.filter((t) => t.cliente_id === cId);
        }
      }
      return sendJson(res, 200, achadas.map(comNomeDaCliente));
    }

    if (req.method === "POST") {
      return getBody(req).then((dados) => {
        const nova = {
          id: tatuagens.length + 1,
          cliente_id: Number(dados.cliente_id),
          ideia: String(dados.ideia || ""),
          local_do_corpo: String(dados.local_do_corpo || ""),
          tamanho: Number(dados.tamanho || 0),
          etapa: "pedida",
        };
        tatuagens.push(nova);
        return sendJson(res, 201, comNomeDaCliente(nova));
      });
    }

    return sendJson(res, 405, { detail: "Método não permitido." });
  }

  return next();
}
