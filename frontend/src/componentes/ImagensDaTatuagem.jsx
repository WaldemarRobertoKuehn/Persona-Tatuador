/* As imagens de uma tatuagem: referências do cliente e o desenho do tatuador.
 *
 * O cliente envia referência e aprova ou recusa o desenho. O tatuador envia o
 * desenho, pode removê-lo e vê o motivo de uma recusa. As duas telas usam este
 * componente, e quem decide quais botões aparecem são as permissões que vieram
 * do login: a tela não repete a regra de quem pode o quê.
 *
 * A imagem é buscada com o token e transformada em object URL. Um <img src="/...">
 * não manda o cabeçalho Authorization, e a rota de download é autenticada.
 */

import { useEffect, useRef, useState } from "react";

import {
  aprovarImagem,
  buscarConteudoImagem,
  buscarImagens,
  enviarImagem,
  recusarImagem,
  removerImagem,
} from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "./Avisos";

/* O mesmo limite do back, repetido aqui só para avisar antes do upload. Quem
 * recusa de verdade continua sendo o servidor. */
const TAMANHO_MAXIMO = 4 * 1024 * 1024;
const TIPOS_ACEITOS = [
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/svg+xml",
];

const ROTULO_DO_STATUS = {
  pendente: "Aguardando aprovação",
  aprovada: "Aprovada",
  recusada: "Recusada",
};

function enderecoDaBuscaNoGoogle(ideia) {
  const termo = [ideia, "tatuagem", "desenho"].filter(Boolean).join(" ");
  return `https://www.google.com/search?tbm=isch&hl=pt-BR&q=${encodeURIComponent(termo)}`;
}

/* A miniatura busca o arquivo uma vez e revoga o object URL ao desmontar, para
 * o navegador não guardar o blob da imagem antiga depois que a tela troca. */
function Miniatura({ tatuagemId, imagem }) {
  const [url, setUrl] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let vivo = true;
    let criado = null;

    buscarConteudoImagem(tatuagemId, imagem.id)
      .then((blob) => {
        if (!vivo) {
          return;
        }

        criado = URL.createObjectURL(blob);
        setUrl(criado);
      })
      .catch((erroRecebido) => {
        if (vivo) {
          setErro(erroRecebido.message);
        }
      });

    return () => {
      vivo = false;

      if (criado) {
        URL.revokeObjectURL(criado);
      }
    };
  }, [tatuagemId, imagem.id]);

  if (erro) {
    return <div className="imagem-sem-preview">Não foi possível carregar.</div>;
  }

  if (!url) {
    return <div className="imagem-sem-preview">Carregando imagem...</div>;
  }

  return <img className="miniatura-da-imagem" src={url} alt={imagem.nome} />;
}

function PreviaDoArquivo({ arquivo }) {
  const [url, setUrl] = useState(null);

  useEffect(() => {
    const criado = URL.createObjectURL(arquivo);
    let vivo = true;

    Promise.resolve().then(() => {
      if (vivo) {
        setUrl(criado);
      }
    });

    return () => {
      vivo = false;
      URL.revokeObjectURL(criado);
    };
  }, [arquivo]);

  if (!url) {
    return null;
  }

  return (
    <img
      className="previa-do-arquivo"
      src={url}
      alt={`Prévia de ${arquivo.name}`}
    />
  );
}

export default function ImagensDaTatuagem({
  tatuagemId,
  ideia = "",
  origem = "",
  perfil,
  aoAtualizarTatuagem,
}) {
  const permissoes = new Set(perfil.permissoes ?? []);
  const podeEnviar = permissoes.has("imagens:enviar");
  const podeRemover = permissoes.has("imagens:remover");
  const ehCliente = perfil.tipo === "cliente";
  const podeDecidirDesenho =
    permissoes.has("imagens:aprovar") &&
    (ehCliente ||
      (perfil.tipo === "administrador" && origem === "presencial"));

  const [imagens, setImagens] = useState([]);
  /* Guarda de qual tatuagem é a lista que está na tela. Enquanto não bater com a
   * tatuagem aberta, o carregando é derivado, sem um setState dentro do efeito. */
  const [imagensDa, setImagensDa] = useState(null);
  const [erro, setErro] = useState("");
  const [erroAcao, setErroAcao] = useState("");
  const [aviso, setAviso] = useState("");
  const [arquivo, setArquivo] = useState(null);
  const [arrastando, setArrastando] = useState(false);
  const [tipo, setTipo] = useState("desenho");
  const [enviando, setEnviando] = useState(false);
  const [acaoId, setAcaoId] = useState(null);
  const [recusandoId, setRecusandoId] = useState(null);
  const [motivo, setMotivo] = useState("");
  const campoArquivo = useRef(null);

  /* A lista que está na tela ainda é de outra tatuagem? Então está carregando. */
  const carregando = imagensDa !== tatuagemId;

  /* Carrega a lista quando a tatuagem muda. O vivo impede a resposta atrasada de
   * uma tatuagem anterior de aparecer na tela da tatuagem atual. */
  useEffect(() => {
    let vivo = true;

    buscarImagens(tatuagemId)
      .then((recebidas) => {
        if (vivo) {
          setImagens(recebidas);
          setImagensDa(tatuagemId);
          setErro("");
        }
      })
      .catch((erroRecebido) => {
        if (vivo) {
          setImagensDa(tatuagemId);
          setErro(erroRecebido.message);
        }
      });

    return () => {
      vivo = false;
    };
  }, [tatuagemId]);

  function recarregarImagens() {
    return buscarImagens(tatuagemId)
      .then((recebidas) => {
        setImagens(recebidas);
        setImagensDa(tatuagemId);
        setErro("");
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message));
  }

  function definirArquivo(escolhido) {
    setErroAcao("");
    setAviso("");

    if (!escolhido) {
      setArquivo(null);
      return;
    }

    if (!TIPOS_ACEITOS.includes(escolhido.type)) {
      setErroAcao("Escolha uma imagem JPEG, PNG, WebP ou SVG.");
      setArquivo(null);
      return;
    }

    if (escolhido.size > TAMANHO_MAXIMO) {
      setErroAcao("A imagem passa do limite de 4 MB. Escolha uma versão menor.");
      setArquivo(null);
      return;
    }

    setArquivo(escolhido);
  }

  function escolherArquivo(evento) {
    definirArquivo(evento.target.files?.[0] ?? null);
    evento.target.value = "";
  }

  function soltarArquivo(evento) {
    evento.preventDefault();
    setArrastando(false);
    definirArquivo(evento.dataTransfer.files?.[0] ?? null);
  }

  function limparArquivo() {
    setArquivo(null);

    if (campoArquivo.current) {
      campoArquivo.current.value = "";
    }
  }

  function enviar(evento) {
    evento.preventDefault();

    if (!arquivo) {
      setErroAcao("Escolha um arquivo antes de enviar.");
      return;
    }

    setEnviando(true);
    setErroAcao("");
    setAviso("");

    enviarImagem(tatuagemId, { arquivo, tipo, nome: arquivo.name })
      .then(() => {
        setAviso("Imagem salva no banco de dados.");
        limparArquivo();
        return recarregarImagens();
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setEnviando(false));
  }

  function aprovar(imagem) {
    setAcaoId(imagem.id);
    setErroAcao("");
    setAviso("");

    aprovarImagem(tatuagemId, imagem.id)
      .then(() => {
        setAviso(
          "Desenho aprovado. Se a tatuagem ainda estava pedida, ela avançou para a etapa desenho aprovado.",
        );
        return recarregarImagens();
      })
      .then(() => {
        if (aoAtualizarTatuagem) {
          return aoAtualizarTatuagem();
        }

        return null;
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setAcaoId(null));
  }

  function confirmarRecusa(imagem) {
    setAcaoId(imagem.id);
    setErroAcao("");
    setAviso("");

    recusarImagem(tatuagemId, imagem.id, motivo)
      .then(() => {
        setAviso(
          podeRemover
            ? "Desenho recusado. Você pode remover a imagem recusada abaixo."
            : "Desenho recusado. O tatuador vai ver o motivo.",
        );
        setRecusandoId(null);
        setMotivo("");
        return recarregarImagens();
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setAcaoId(null));
  }

  function remover(imagem) {
    setAcaoId(imagem.id);
    setErroAcao("");
    setAviso("");

    removerImagem(tatuagemId, imagem.id)
      .then(() => {
        setAviso("Imagem removida.");
        return recarregarImagens();
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setAcaoId(null));
  }

  return (
    <section className="bloco-de-imagens">
      <div className="titulo-do-bloco">
        <h3>Desenho e referências</h3>
        {!carregando && !erro ? (
          <span className="legenda">
            {imagens.length === 1 ? "1 imagem" : `${imagens.length} imagens`}
          </span>
        ) : null}
      </div>

      {carregando ? <AvisoCarregando oQue="as imagens" /> : null}

      {!carregando && erro ? <AvisoErro erro={erro} /> : null}

      {!carregando && !erro && imagens.length === 0 ? (
        <AvisoVazio>
          Nenhuma imagem ainda. O cliente envia o desenho e aprova. No
          presencial, o administrador escolhe e autoriza.
        </AvisoVazio>
      ) : null}

      {!carregando && !erro && imagens.length > 0 ? (
        <div className="grade-de-imagens">
          {imagens.map((imagem) => {
            const ehDesenho = imagem.tipo === "desenho";
            const podeDecidir = podeDecidirDesenho && ehDesenho;
            const podeRemoverImagem =
              podeRemover && (!ehCliente || imagem.status === "recusada");

            return (
              <article key={imagem.id} className="cartao-de-imagem">
                <Miniatura tatuagemId={tatuagemId} imagem={imagem} />

                <div className="dados-da-imagem">
                  <strong>{imagem.nome}</strong>
                  <span className="legenda">
                    {ehDesenho ? "Desenho" : "Referência"}
                  </span>
                  {ehDesenho ? (
                    <span
                      className="etiqueta-status"
                      data-status={imagem.status}
                    >
                      {ROTULO_DO_STATUS[imagem.status] ?? imagem.status}
                    </span>
                  ) : null}

                  {imagem.motivo_recusa ? (
                    <p className="legenda">
                      Motivo da recusa: {imagem.motivo_recusa}
                    </p>
                  ) : null}
                </div>

                {podeDecidir && imagem.status !== "aprovada" ? (
                  recusandoId === imagem.id ? (
                    <div className="acao-da-imagem">
                      <textarea
                        value={motivo}
                        onChange={(evento) => setMotivo(evento.target.value)}
                        maxLength={500}
                        placeholder="Por que este desenho não serve?"
                        aria-label="Motivo da recusa"
                      />
                      <div className="linha-de-botoes">
                        <button
                          type="button"
                          className="botao"
                          disabled={acaoId !== null}
                          onClick={() => confirmarRecusa(imagem)}
                        >
                          {acaoId === imagem.id ? "Enviando..." : "Enviar recusa"}
                        </button>
                        <button
                          type="button"
                          className="botao-neutro"
                          onClick={() => {
                            setRecusandoId(null);
                            setMotivo("");
                          }}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="linha-de-botoes">
                      <button
                        type="button"
                        className="botao"
                        disabled={acaoId !== null}
                        onClick={() => aprovar(imagem)}
                      >
                        {acaoId === imagem.id ? "Aprovando..." : "Aprovar desenho"}
                      </button>
                      <button
                        type="button"
                        className="botao-neutro"
                        onClick={() => {
                          setRecusandoId(imagem.id);
                          setMotivo("");
                        }}
                      >
                        Recusar
                      </button>
                    </div>
                  )
                ) : null}

                {podeRemoverImagem ? (
                  <button
                    type="button"
                    className="botao-neutro"
                    disabled={acaoId !== null}
                    onClick={() => remover(imagem)}
                  >
                    {acaoId === imagem.id
                      ? "Removendo..."
                      : imagem.status === "recusada"
                        ? "Remover desenho recusado"
                        : "Remover imagem"}
                  </button>
                ) : null}
              </article>
            );
          })}
        </div>
      ) : null}

      {erroAcao ? (
        <p className="mensagem-erro" role="alert">
          {erroAcao}
        </p>
      ) : null}

      {aviso ? (
        <p className="confirmacao" role="status">
          {aviso}
        </p>
      ) : null}

      {podeEnviar ? (
        <form className="formulario-de-imagem" onSubmit={enviar}>
          <h4>Buscar ou enviar imagem</h4>

          <a
            className="botao botao-largo"
            href={enderecoDaBuscaNoGoogle(ideia)}
            target="_blank"
            rel="noopener noreferrer"
          >
            Escolher desenho no Google
          </a>

          <p className="legenda">
            A busca abre o Google Imagens em outra aba. Baixe o desenho e
            arraste o arquivo para a área abaixo.
          </p>

          <input
            ref={campoArquivo}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/svg+xml"
            onChange={escolherArquivo}
            hidden
          />

          <div
            className="area-de-soltura"
            data-arrastando={arrastando ? "true" : "false"}
            role="button"
            tabIndex={0}
            aria-label="Soltar ou escolher uma imagem"
            onClick={() => campoArquivo.current?.click()}
            onKeyDown={(evento) => {
              if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                campoArquivo.current?.click();
              }
            }}
            onDragOver={(evento) => {
              evento.preventDefault();
              setArrastando(true);
            }}
            onDragLeave={(evento) => {
              if (!evento.currentTarget.contains(evento.relatedTarget)) {
                setArrastando(false);
              }
            }}
            onDrop={soltarArquivo}
          >
            {arquivo ? <PreviaDoArquivo arquivo={arquivo} /> : null}
            <strong>
              {arquivo
                ? arquivo.name
                : "Arraste o desenho baixado do Google aqui"}
            </strong>
            <span className="legenda">
              {arquivo
                ? "Clique na área para trocar a imagem."
                : "Ou clique para escolher uma foto do computador."}
            </span>
          </div>

          {arquivo ? (
            <button
              type="button"
              className="link-acao"
              onClick={limparArquivo}
            >
              Escolher outro arquivo
            </button>
          ) : null}

          <label className="campo">
            <span>Tipo</span>
            <select
              value={tipo}
              onChange={(evento) => setTipo(evento.target.value)}
            >
              <option value="desenho">Desenho</option>
              <option value="referencia">Referência</option>
            </select>
          </label>

          <p className="legenda">
            JPEG, PNG, WebP ou SVG, até 4 MB. O cliente escolhe e envia o
            desenho para o tatuador e aprova a arte. No presencial, o
            administrador escolhe e autoriza.
          </p>

          <button
            type="submit"
            className="botao"
            disabled={enviando || !arquivo}
          >
            {enviando ? "Salvando..." : "Salvar imagem"}
          </button>
        </form>
      ) : null}
    </section>
  );
}
