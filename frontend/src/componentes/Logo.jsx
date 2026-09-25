/* O logo do estúdio, no cabeçalho das telas.
 *
 * A imagem vem de docs/marca/logo.svg, que é onde a REGRAS manda que a marca
 * fique. O Vite serve aquela pasta como arquivo estático, então este componente
 * não tem cópia do logo dentro do front: se a linha do logo mudar de espessura,
 * muda no arquivo de origem e a tela acompanha.
 *
 * Por que a tag img e não um h1 com o nome escrito: o logo é uma imagem, e
 * escrever o nome com a fonte do site não seria o logo, seria um texto parecido
 * com ele. E o alt não é opcional aqui. Quem usa leitor de tela não vê a
 * imagem, e sem o alt a pessoa ouviria o nome do arquivo.
 *
 * A largura de 160 px respeita a regra do marca.md de que abaixo de 120 px de
 * largura o logo vira borra e quem deveria aparecer é o símbolo. A altura vai
 * junto na mesma proporção, 250 por 71, porque esticar o logo é proibido pela
 * marca. Se a caixa do SVG mudar, estes dois números mudam com ela: são a mesma
 * proporção, e é isso que impede o navegador de achatar a imagem.
 *
 * No tema escuro o componente pede o outro arquivo da marca, o logo-escuro.svg,
 * que já foi desenhado com a palavra em branco. Trocar de arquivo e não
 * repintar por CSS é o que a marca exige: um logo que mudasse de cor conforme o
 * fundo seria uma versão que ninguém desenhou. Como o alt é o mesmo nos dois
 * casos, quem usa leitor de tela ouve a mesma coisa em qualquer tema. */
export default function Logo({ escuro = false }) {
  return (
    <img
      className="logo"
      src={escuro ? "/logo-escuro.svg" : "/logo.svg"}
      alt="Traço Fino, estúdio de tatuagem"
      width="160"
      height="45"
    />
  );
}
