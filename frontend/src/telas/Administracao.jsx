/* A administração da equipe e da carteira de tatuagens.
 *
 * Duas operações moram aqui: cadastrar um tatuador e trocar quem responde pela
 * agenda de uma tatuagem. As duas são administrativas, e o back é quem confere a
 * permissão; a tela só desenha o que o grupo Administrador pode fazer.
 */

import { useEffect, useState } from "react";

import {
  atribuirTatuador,
  buscarTatuadores,
  buscarTatuagens,
  cadastrarTatuador,
} from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "../componentes/Avisos";
import CabecalhoDaTela from "../componentes/CabecalhoDaTela";
import Etiqueta from "../componentes/Etiqueta";

const FORMULARIO_VAZIO = { nome: "", email: "", senha: "" };

export default function Administracao({ perfil }) {
  const [tatuadores, setTatuadores] = useState([]);
  const [estadoTatuadores, setEstadoTatuadores] = useState("carregando");
  const [erroTatuadores, setErroTatuadores] = useState("");

  const [tatuagens, setTatuagens] = useState([]);
  const [estadoTatuagens, setEstadoTatuagens] = useState("carregando");
  const [erroTatuagens, setErroTatuagens] = useState("");

  const [formulario, setFormulario] = useState(FORMULARIO_VAZIO);
  const [cadastrando, setCadastrando] = useState(false);
  const [erroCadastro, setErroCadastro] = useState("");
  const [confirmacaoCadastro, setConfirmacaoCadastro] = useState("");

  const [salvandoTatuagem, setSalvandoTatuagem] = useState(null);
  const [erroAtribuicao, setErroAtribuicao] = useState("");
  const [confirmacaoAtribuicao, setConfirmacaoAtribuicao] = useState("");

  function carregarTatuadores() {
    return buscarTatuadores()
      .then((recebidos) => {
        setTatuadores(recebidos);
        setEstadoTatuadores("pronto");
        setErroTatuadores("");
      })
      .catch((erroRecebido) => {
        setErroTatuadores(erroRecebido.message);
        setEstadoTatuadores("erro");
      });
  }

  function carregarTatuagens() {
    return buscarTatuagens()
      .then((recebidas) => {
        setTatuagens(recebidas);
        setEstadoTatuagens("pronto");
        setErroTatuagens("");
      })
      .catch((erroRecebido) => {
        setErroTatuagens(erroRecebido.message);
        setEstadoTatuagens("erro");
      });
  }

  useEffect(() => {
    carregarTatuadores();
    carregarTatuagens();
  }, []);

  function mudar(campo, valor) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function enviar(evento) {
    evento.preventDefault();

    setCadastrando(true);
    setErroCadastro("");
    setConfirmacaoCadastro("");

    cadastrarTatuador(formulario)
      .then((novo) => {
        setFormulario(FORMULARIO_VAZIO);
        setConfirmacaoCadastro(
          `${novo.nome} agora faz parte da equipe de tatuadores. ` +
            `Usuário de acesso: ${novo.usuario}.`,
        );
        return carregarTatuadores();
      })
      .catch((erroRecebido) => setErroCadastro(erroRecebido.message))
      .finally(() => setCadastrando(false));
  }

  function trocarResponsavel(tatuagem, tatuadorId) {
    setSalvandoTatuagem(tatuagem.id);
    setErroAtribuicao("");
    setConfirmacaoAtribuicao("");

    atribuirTatuador(tatuagem.id, Number(tatuadorId))
      .then((atualizada) => {
        setTatuagens((anteriores) =>
          anteriores.map((item) =>
            item.id === atualizada.id ? atualizada : item,
          ),
        );
        setConfirmacaoAtribuicao(
          atualizada.tatuador_nome
            ? `A tatuagem ${atualizada.id} agora é de ${atualizada.tatuador_nome}.`
            : `A tatuagem ${atualizada.id} ficou sem tatuador responsável.`,
        );
      })
      .catch((erroRecebido) => setErroAtribuicao(erroRecebido.message))
      .finally(() => setSalvandoTatuagem(null));
  }

  return (
    <main className="tela">
      <CabecalhoDaTela
        titulo="Administração"
        apoio={`${perfil.nome}, cadastre tatuadores e defina quem responde pela agenda de cada tatuagem.`}
      />

      <div className="secoes-da-ficha">
        <section className="cartao">
          <h2>Equipe de tatuadores</h2>
          <p className="legenda legenda-folgada">
            A conta nasce no grupo tatuador, com as permissões de agenda e de
            imagens. A pessoa recebe um email de confirmação no endereço
            cadastrado.
          </p>

          {estadoTatuadores === "carregando" ? (
            <AvisoCarregando oQue="os tatuadores" />
          ) : null}
          {estadoTatuadores === "erro" ? (
            <AvisoErro erro={erroTatuadores} />
          ) : null}

          {estadoTatuadores === "pronto" ? (
            tatuadores.length === 0 ? (
              <AvisoVazio>Nenhum tatuador cadastrado ainda.</AvisoVazio>
            ) : (
              <ul className="lista-cartoes">
                {tatuadores.map((tatuador) => (
                  <li key={tatuador.id} className="cartao-de-imagem">
                    <strong>{tatuador.nome}</strong>
                    <span className="legenda">{tatuador.email}</span>
                  </li>
                ))}
              </ul>
            )
          ) : null}

          <form className="formulario-de-equipe" onSubmit={enviar}>
            <h4>Cadastrar novo tatuador</h4>

            <div className="par">
              <label className="campo">
                <span>Nome</span>
                <input
                  name="nome"
                  value={formulario.nome}
                  onChange={(evento) => mudar("nome", evento.target.value)}
                  minLength={2}
                  maxLength={100}
                  required
                />
              </label>

              <label className="campo">
                <span>Email</span>
                <input
                  name="email"
                  type="email"
                  value={formulario.email}
                  onChange={(evento) => mudar("email", evento.target.value)}
                  maxLength={254}
                  required
                />
              </label>
            </div>

            <label className="campo">
              <span>Senha inicial</span>
              <input
                name="senha"
                type="password"
                value={formulario.senha}
                onChange={(evento) => mudar("senha", evento.target.value)}
                minLength={8}
                maxLength={128}
                autoComplete="new-password"
                required
              />
            </label>

            {erroCadastro ? (
              <p className="mensagem-erro" role="alert">
                {erroCadastro}
              </p>
            ) : null}
            {confirmacaoCadastro ? (
              <p className="confirmacao" role="status">
                {confirmacaoCadastro}
              </p>
            ) : null}

            <button type="submit" className="botao" disabled={cadastrando}>
              {cadastrando ? "Cadastrando..." : "Cadastrar tatuador"}
            </button>
          </form>
        </section>

        <section className="cartao">
          <h2>Tatuador responsável</h2>
          <p className="legenda legenda-folgada">
            A agenda de cada tatuagem pertence ao profissional escolhido aqui.
            Trocar o responsável move a agenda inteira, inclusive os horários já
            marcados.
          </p>

          {estadoTatuagens === "carregando" ? (
            <AvisoCarregando oQue="as tatuagens" />
          ) : null}
          {estadoTatuagens === "erro" ? (
            <AvisoErro erro={erroTatuagens} />
          ) : null}

          {erroAtribuicao ? (
            <p className="mensagem-erro" role="alert">
              {erroAtribuicao}
            </p>
          ) : null}
          {confirmacaoAtribuicao ? (
            <p className="confirmacao" role="status">
              {confirmacaoAtribuicao}
            </p>
          ) : null}

          {estadoTatuagens === "pronto" ? (
            tatuagens.length === 0 ? (
              <AvisoVazio>Nenhuma tatuagem pedida ainda.</AvisoVazio>
            ) : (
              <table className="tabela">
                <thead>
                  <tr>
                    <th scope="col">Tatuagem</th>
                    <th scope="col">Cliente</th>
                    <th scope="col">Etapa</th>
                    <th scope="col">Tatuador</th>
                  </tr>
                </thead>
                <tbody>
                  {tatuagens.map((tatuagem) => (
                    <tr key={tatuagem.id}>
                      <td data-rotulo="Tatuagem">
                        #{tatuagem.id} · {tatuagem.ideia}
                      </td>
                      <td data-rotulo="Cliente">{tatuagem.nome_da_cliente}</td>
                      <td data-rotulo="Etapa">
                        <Etiqueta etapa={tatuagem.etapa} />
                      </td>
                      <td data-rotulo="Tatuador">
                        <select
                          className="seletor-de-tatuador"
                          value={tatuagem.tatuador_id ?? ""}
                          disabled={
                            tatuadores.length === 0 ||
                            salvandoTatuagem !== null
                          }
                          onChange={(evento) =>
                            trocarResponsavel(tatuagem, evento.target.value)
                          }
                        >
                          <option value="">Sem tatuador</option>
                          {tatuadores.map((tatuador) => (
                            <option key={tatuador.id} value={tatuador.id}>
                              {tatuador.nome}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : null}

          {estadoTatuagens === "pronto" && tatuadores.length === 0 ? (
            <p className="legenda">
              Cadastre pelo menos um tatuador para poder atribuir a
              responsabilidade.
            </p>
          ) : null}
        </section>
      </div>
    </main>
  );
}
