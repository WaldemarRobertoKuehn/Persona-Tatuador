/* A miniatura do desenho de uma tatuagem na lista da agenda.
 *
 * A rota de download é autenticada, então o <img> não pode apontar direto para
 * ela: o navegador não manda o cabeçalho Authorization. O componente busca o
 * arquivo com o token e cria um object URL, que é revogado ao desmontar para o
 * blob não ficar preso na memória.
 *
 * O estado guarda de qual imagem é o resultado. Enquanto a imagem na tela não
 * for a que está na tatuagem, o componente mostra o espaço vazio, sem precisar
 * de um setState síncrono dentro do efeito para "voltar a carregar".
 */

import { useEffect, useState } from "react";

import { buscarConteudoImagem } from "../api";

export default function MiniaturaDoDesenho({ tatuagemId, imagemId }) {
  /* { imagemId, url } quando carregou, { imagemId, erro: true } quando falhou. */
  const [resultado, setResultado] = useState(null);

  const atual = resultado?.imagemId === imagemId ? resultado : null;
  const url = atual?.url ?? null;
  const erro = Boolean(atual?.erro);

  useEffect(() => {
    if (!imagemId) {
      return undefined;
    }

    let vivo = true;
    let criado = null;

    buscarConteudoImagem(tatuagemId, imagemId)
      .then((blob) => {
        if (!vivo) {
          return;
        }

        criado = URL.createObjectURL(blob);
        setResultado({ imagemId, url: criado });
      })
      .catch(() => {
        if (vivo) {
          setResultado({ imagemId, erro: true });
        }
      });

    return () => {
      vivo = false;

      if (criado) {
        URL.revokeObjectURL(criado);
      }
    };
  }, [tatuagemId, imagemId]);

  if (!imagemId) {
    return <div className="sem-miniatura-da-agenda">Sem desenho</div>;
  }

  if (erro) {
    return <div className="sem-miniatura-da-agenda">Não carregou</div>;
  }

  if (!url) {
    return <div className="sem-miniatura-da-agenda">...</div>;
  }

  return (
    <img
      className="miniatura-da-agenda"
      src={url}
      alt="Desenho da tatuagem"
    />
  );
}
