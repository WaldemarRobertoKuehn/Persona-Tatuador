import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Depósitos em memória (conforme a regra da cartilha)
interface Cliente {
  id: number;
  nome: string;
}

interface Tatuagem {
  id: number;
  cliente_id: number;
  ideia: string;
  local_do_corpo: string;
  tamanho: number;
  etapa: string;
}

interface Passo {
  id: number;
  tatuagem_id: number;
  tipo: string;
  data: string;
  observacao: string;
}

const clientes: Cliente[] = [
  { id: 1, nome: "Bruna" },
  { id: 2, nome: "Camila" },
];

const tatuagens: Tatuagem[] = [
  {
    id: 1,
    cliente_id: 1,
    ideia: "ramo de cerejeira no antebraço",
    local_do_corpo: "antebraço",
    tamanho: 12.5,
    etapa: "finalizada",
  },
  {
    id: 2,
    cliente_id: 1,
    ideia: "serpente enrolada na canela",
    local_do_corpo: "canela",
    tamanho: 20.0,
    etapa: "em sessões",
  },
  {
    id: 3,
    cliente_id: 2,
    ideia: "rosa no pulso esquerdo",
    local_do_corpo: "pulso",
    tamanho: 7.0,
    etapa: "desenho aprovado",
  },
  {
    id: 4,
    cliente_id: 1,
    ideia: "casa no porta-retrato da coxa",
    local_do_corpo: "coxa",
    tamanho: 15.0,
    etapa: "pedida",
  },
  {
    id: 5,
    cliente_id: 2,
    ideia: "texto 'não desista' no antebraço",
    local_do_corpo: "antebraço",
    tamanho: 9.0,
    etapa: "em sessões",
  },
  {
    id: 6,
    cliente_id: 1,
    ideia: "folha de figueira na costela",
    local_do_corpo: "costela",
    tamanho: 14.0,
    etapa: "em sessões",
  },
  {
    id: 7,
    cliente_id: 1,
    ideia: "onda quebrando no tornozelo",
    local_do_corpo: "tornozelo",
    tamanho: 6.5,
    etapa: "desenho aprovado",
  },
  {
    id: 8,
    cliente_id: 2,
    ideia: "três pontos no ombro, como mapa",
    local_do_corpo: "ombro",
    tamanho: 5.0,
    etapa: "pedida",
  },
];

const passos: Passo[] = [
  {
    id: 1,
    tatuagem_id: 1,
    tipo: "desenho aprovado",
    data: "2026-08-03",
    observacao: "a cliente aprovou o desenho, sem ajuste",
  },
  {
    id: 2,
    tatuagem_id: 1,
    tipo: "sessão",
    data: "2026-08-10",
    observacao: "contorno com linha fina, sem preenchimento",
  },
  {
    id: 3,
    tatuagem_id: 1,
    tipo: "sessão",
    data: "2026-08-17",
    observacao: "preenchimento do fundo e ajuste de traço",
  },
  {
    id: 4,
    tatuagem_id: 1,
    tipo: "retoque",
    data: "2026-09-14",
    observacao: "retoque na ponta de um pétala",
  },
  {
    id: 5,
    tatuagem_id: 2,
    tipo: "desenho aprovado",
    data: "2026-09-01",
    observacao: "aprovado depois de duas mudanças no desenho",
  },
  {
    id: 6,
    tatuagem_id: 2,
    tipo: "sessão",
    data: "2026-09-08",
    observacao: "primeira sessão, só a linha",
  },
  {
    id: 7,
    tatuagem_id: 3,
    tipo: "desenho aprovado",
    data: "2026-09-15",
    observacao: "desenho aprovado, a tatuagem entra na fila das sessões",
  },
  {
    id: 8,
    tatuagem_id: 5,
    tipo: "desenho aprovado",
    data: "2026-09-05",
    observacao: "texto na fonte escolhida pela cliente",
  },
  {
    id: 9,
    tatuagem_id: 5,
    tipo: "sessão",
    data: "2026-09-12",
    observacao: "rascunho da letra",
  },
  {
    id: 10,
    tatuagem_id: 5,
    tipo: "sessão",
    data: "2026-09-19",
    observacao: "letra fechada, aguardando a cicatrização para o retoque",
  },
  {
    id: 11,
    tatuagem_id: 6,
    tipo: "desenho aprovado",
    data: "2026-09-08",
    observacao: "a cliente pediu a folha menor que a primeira versão",
  },
  {
    id: 12,
    tatuagem_id: 6,
    tipo: "sessão",
    data: "2026-09-22",
    observacao: "contorno e primeira parte do sombreado da folha",
  },
  {
    id: 13,
    tatuagem_id: 7,
    tipo: "desenho aprovado",
    data: "2026-09-24",
    observacao: "onda aprovada, entra na fila das sessões",
  },
];

const REGRAS_DE_PASSO: Record<string, { etapas_aceitas: string[]; etapa_nova: string }> = {
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

function comNomeDaCliente(tatuagem: Tatuagem) {
  const cliente = clientes.find((c) => c.id === tatuagem.cliente_id);
  const nome = cliente ? cliente.nome : `cliente ${tatuagem.cliente_id}`;
  return { ...tatuagem, nome_da_cliente: nome };
}

async function startServer() {
  const app = express();
  const PORT = Number(process.env.PORT) || 3000;
  const isProduction = process.env.NODE_ENV === 'production';

  app.use(express.json());

  // Rotas de Tatuagens
  app.get('/tatuagens', (req, res) => {
    let filtradas = [...tatuagens];

    if (req.query.etapa && typeof req.query.etapa === 'string') {
      filtradas = filtradas.filter((t) => t.etapa === req.query.etapa);
    }

    if (req.query.cliente_id) {
      const clienteId = Number(req.query.cliente_id);
      filtradas = filtradas.filter((t) => t.cliente_id === clienteId);
    }

    res.json(filtradas.map(comNomeDaCliente));
  });

  app.post('/tatuagens', (req, res) => {
    const { cliente_id, ideia, local_do_corpo, tamanho } = req.body || {};

    if (
      !cliente_id ||
      typeof cliente_id !== 'number' ||
      cliente_id <= 0 ||
      !ideia ||
      typeof ideia !== 'string' ||
      ideia.trim().length < 10 ||
      ideia.trim().length > 500 ||
      !local_do_corpo ||
      typeof local_do_corpo !== 'string' ||
      local_do_corpo.trim().length < 2 ||
      local_do_corpo.trim().length > 80 ||
      typeof tamanho !== 'number' ||
      tamanho <= 0
    ) {
      return res.status(422).json({
        detail: "Dados inválidos para o pedido de tatuagem.",
      });
    }

    const nova: Tatuagem = {
      id: tatuagens.length + 1,
      cliente_id,
      ideia: ideia.trim(),
      local_do_corpo: local_do_corpo.trim(),
      tamanho,
      etapa: "pedida",
    };

    tatuagens.push(nova);
    res.status(201).json(comNomeDaCliente(nova));
  });

  app.get('/tatuagens/:tatuagem_id', (req, res) => {
    const id = Number(req.params.tatuagem_id);
    const tatuagem = tatuagens.find((t) => t.id === id);

    if (!tatuagem) {
      return res.status(404).json({ detail: "Tatuagem não encontrada." });
    }

    res.json(comNomeDaCliente(tatuagem));
  });

  // Rotas de Passos
  app.get('/tatuagens/:tatuagem_id/passos', (req, res) => {
    const id = Number(req.params.tatuagem_id);
    const tatuagem = tatuagens.find((t) => t.id === id);

    if (!tatuagem) {
      return res.status(404).json({ detail: "Tatuagem não encontrada." });
    }

    const passosDaTatuagem = passos.filter((p) => p.tatuagem_id === id);
    res.json(passosDaTatuagem);
  });

  app.post('/tatuagens/:tatuagem_id/passos', (req, res) => {
    const id = Number(req.params.tatuagem_id);
    const tatuagem = tatuagens.find((t) => t.id === id);

    if (!tatuagem) {
      return res.status(404).json({ detail: "Tatuagem não encontrada." });
    }

    const { tipo, observacao = "" } = req.body || {};

    if (!tipo || typeof tipo !== 'string' || !REGRAS_DE_PASSO[tipo]) {
      return res.status(422).json({
        detail: `'${tipo}' não é um passo deste estúdio. Os passos são: desenho aprovado, sessão e retoque.`,
      });
    }

    const regra = REGRAS_DE_PASSO[tipo];

    if (!regra.etapas_aceitas.includes(tatuagem.etapa)) {
      return res.status(422).json({
        detail: `Não dá para registrar '${tipo}' agora: a tatuagem está '${tatuagem.etapa}', e esse passo só entra em tatuagem que esteja em: ${regra.etapas_aceitas.join(", ")}.`,
      });
    }

    const hoje = new Date().toISOString().split("T")[0];
    const novoPasso: Passo = {
      id: passos.length + 1,
      tatuagem_id: id,
      tipo,
      data: hoje,
      observacao: typeof observacao === 'string' ? observacao.trim() : "",
    };

    passos.push(novoPasso);
    tatuagem.etapa = regra.etapa_nova;

    res.status(201).json(novoPasso);
  });

  // Servir arquivos de marca
  app.use(express.static(path.resolve(__dirname, 'docs/marca')));

  // Em desenvolvimento, montar os middlewares do Vite
  if (!isProduction) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.resolve(__dirname, 'dist')));
    app.get('*', (_req, res) => {
      res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Traço Fino server running on port ${PORT}`);
  });
}

startServer();
