/* A agenda de uma tatuagem: sessões e o retoque final.
 *
 * O cliente consulta os horários marcados. O tatuador marca, cancela e vê os
 * blocos livres do dia. A disponibilidade vem pronta do back, porque quem sabe
 * o expediente e os horários ocupados é o servidor; a tela só desenha os botões.
 *
 * A agenda é do tatuador responsável pela tatuagem, então o bloqueio de horário
 * não é do estúdio inteiro.
 */

import { useEffect, useState } from "react";

import {
  buscarAgendamentos,
  buscarDisponibilidade,
  cancelarAgendamento,
  criarAgendamento,
} from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "./Avisos";
import { dataLocalISO, formatarData, formatarHora } from "../datas";

const TIPOS_DE_AGENDAMENTO = ["sessão", "retoque"];

/* As mesmas etapas que o serviço aceita. A lista aqui só decide se o formulário
 * aparece; a recusa de verdade continua sendo do back. */
const ETAPAS_QUE_AGENDAM = new Set(["desenho aprovado", "em sessões"]);

const ROTULO_DO_STATUS = {
  agendado: "Agendado",
  cancelado: "Cancelado",
};

export default function AgendaDaTatuagem({
  tatuagemId,
  tatuadorId,
  etapa,
  perfil,
}) {
  const permissoes = new Set(perfil.permissoes ?? []);
  const podeGerenciar = permissoes.has("agendamentos:gerenciar");
  const podeConsultar = permissoes.has("agendamentos:consultar");

  /* A agenda é do tatuador responsável. Outro tatuador pode consultar os
   * horários, mas não marca nem cancela: quem decide isso no servidor é o
   * serviço, e a tela esconde o formulário para não oferecer uma ação que o
   * back vai recusar. */
  const ehResponsavel =
    perfil.tipo !== "tatuador" || perfil.usuarioId === tatuadorId;
  const podeGerenciarEstaAgenda = podeGerenciar && ehResponsavel;
  const podeAgendar =
    podeGerenciarEstaAgenda && ETAPAS_QUE_AGENDAM.has(etapa);

  const [agendamentos, setAgendamentos] = useState([]);
  const [agendamentosDa, setAgendamentosDa] = useState(null);
  const [erro, setErro] = useState("");
  const [erroAcao, setErroAcao] = useState("");
  const [aviso, setAviso] = useState("");

  const [dataSelecionada, setDataSelecionada] = useState(() => dataLocalISO());
  const [tipo, setTipo] = useState("sessão");
  const [disponibilidade, setDisponibilidade] = useState(null);
  const [disponibilidadeDa, setDisponibilidadeDa] = useState(null);
  const [erroHorarios, setErroHorarios] = useState("");
  const [acaoId, setAcaoId] = useState(null);

  /* O carregando é derivado da data/tatuagem que está na tela, sem um setState
   * síncrono dentro do efeito. */
  const carregandoAgenda = agendamentosDa !== tatuagemId;
  const carregandoHorarios =
    podeAgendar &&
    Boolean(dataSelecionada) &&
    disponibilidadeDa !== dataSelecionada;

  /* Carrega a lista de agendamentos quando a tatuagem muda. */
  useEffect(() => {
    if (!podeConsultar && !podeGerenciar) {
      return undefined;
    }

    let vivo = true;

    buscarAgendamentos(tatuagemId)
      .then((recebidos) => {
        if (vivo) {
          setAgendamentos(recebidos);
          setAgendamentosDa(tatuagemId);
          setErro("");
        }
      })
      .catch((erroRecebido) => {
        if (vivo) {
          setAgendamentosDa(tatuagemId);
          setErro(erroRecebido.message);
        }
      });

    return () => {
      vivo = false;
    };
  }, [tatuagemId, podeConsultar, podeGerenciar]);

  /* Carrega os horários do dia escolhido. Só o tatuador precisa deles, porque é
   * ele quem marca; o cliente lê a lista de agendamentos. */
  useEffect(() => {
    if (!podeAgendar || !dataSelecionada) {
      return undefined;
    }

    let vivo = true;

    buscarDisponibilidade(tatuagemId, dataSelecionada)
      .then((recebida) => {
        if (vivo) {
          setDisponibilidade(recebida);
          setDisponibilidadeDa(dataSelecionada);
          setErroHorarios("");
        }
      })
      .catch((erroRecebido) => {
        if (vivo) {
          setDisponibilidadeDa(dataSelecionada);
          setErroHorarios(erroRecebido.message);
        }
      });

    return () => {
      vivo = false;
    };
  }, [tatuagemId, dataSelecionada, podeAgendar]);

  function recarregarAgendamentos() {
    return buscarAgendamentos(tatuagemId)
      .then((recebidos) => {
        setAgendamentos(recebidos);
        setAgendamentosDa(tatuagemId);
        setErro("");
      })
      .catch((erroRecebido) => setErro(erroRecebido.message));
  }

  function recarregarHorarios() {
    if (!dataSelecionada) {
      return Promise.resolve();
    }

    return buscarDisponibilidade(tatuagemId, dataSelecionada)
      .then((recebida) => {
        setDisponibilidade(recebida);
        setDisponibilidadeDa(dataSelecionada);
        setErroHorarios("");
      })
      .catch((erroRecebido) => setErroHorarios(erroRecebido.message));
  }

  function marcar(horario) {
    setAcaoId(horario.hora_inicio);
    setErroAcao("");
    setAviso("");

    criarAgendamento(tatuagemId, {
      tipo,
      data: dataSelecionada,
      hora_inicio: horario.hora_inicio,
    })
      .then(() => {
        setAviso(
          `Horário marcado para ${formatarData(dataSelecionada)} às ${formatarHora(horario.hora_inicio)} (${tipo}).`,
        );
        return Promise.all([recarregarAgendamentos(), recarregarHorarios()]);
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setAcaoId(null));
  }

  function cancelar(agendamento) {
    setAcaoId(agendamento.id);
    setErroAcao("");
    setAviso("");

    cancelarAgendamento(tatuagemId, agendamento.id)
      .then(() => {
        setAviso("Agendamento cancelado. O horário voltou a ficar livre.");
        return Promise.all([recarregarAgendamentos(), recarregarHorarios()]);
      })
      .catch((erroRecebido) => setErroAcao(erroRecebido.message))
      .finally(() => setAcaoId(null));
  }

  if (!podeConsultar && !podeGerenciar) {
    return null;
  }

  return (
    <section className="bloco-de-agenda">
      <div className="titulo-do-bloco">
        <h3>Agenda</h3>
        {!carregandoAgenda && !erro ? (
          <span className="legenda">
            {agendamentos.length === 1
              ? "1 horário"
              : `${agendamentos.length} horários`}
          </span>
        ) : null}
      </div>

      {carregandoAgenda ? <AvisoCarregando oQue="a agenda" /> : null}

      {!carregandoAgenda && erro ? <AvisoErro erro={erro} /> : null}

      {!carregandoAgenda && !erro && agendamentos.length === 0 ? (
        <AvisoVazio>Nenhum horário marcado ainda.</AvisoVazio>
      ) : null}

      {!carregandoAgenda && !erro && agendamentos.length > 0 ? (
        <ul className="lista-de-agendamentos">
          {agendamentos.map((agendamento) => (
            <li
              key={agendamento.id}
              className="agendamento"
              data-status={agendamento.status}
            >
              <div className="dados-do-agendamento">
                <strong>
                  {formatarData(agendamento.data)} ·{" "}
                  {formatarHora(agendamento.hora_inicio)} às{" "}
                  {formatarHora(agendamento.hora_fim)}
                </strong>
                <span className="legenda">
                  {agendamento.tipo} · {agendamento.tatuador_nome}
                </span>
              </div>

              <span
                className="etiqueta-status"
                data-status={agendamento.status}
              >
                {ROTULO_DO_STATUS[agendamento.status] ?? agendamento.status}
              </span>

              {podeGerenciarEstaAgenda && agendamento.status === "agendado" ? (
                <button
                  type="button"
                  className="botao-neutro"
                  disabled={acaoId !== null}
                  onClick={() => cancelar(agendamento)}
                >
                  {acaoId === agendamento.id ? "Cancelando..." : "Cancelar"}
                </button>
              ) : null}
            </li>
          ))}
        </ul>
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

      {podeAgendar ? (
        <div className="marcador-de-horario">
          <h4>Marcar sessão ou retoque</h4>

          <div className="linha-de-campos">
            <label className="campo">
              <span>Dia</span>
              <input
                type="date"
                value={dataSelecionada}
                min={dataLocalISO()}
                onChange={(evento) => {
                  setDataSelecionada(evento.target.value);
                  setErroAcao("");
                  setAviso("");
                }}
              />
            </label>

            <label className="campo">
              <span>Tipo</span>
              <select
                value={tipo}
                onChange={(evento) => setTipo(evento.target.value)}
              >
                {TIPOS_DE_AGENDAMENTO.map((nome) => (
                  <option key={nome} value={nome}>
                    {nome}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {carregandoHorarios ? (
            <AvisoCarregando oQue="os horários" />
          ) : null}

          {erroHorarios ? <AvisoErro erro={erroHorarios} /> : null}

          {disponibilidade && !carregandoHorarios && !erroHorarios ? (
            disponibilidade.aberto ? (
              <div className="grade-de-horarios">
                {disponibilidade.horarios.map((horario) => (
                  <button
                    key={horario.hora_inicio}
                    type="button"
                    className="horario"
                    data-disponivel={horario.disponivel}
                    disabled={!horario.disponivel || acaoId !== null}
                    onClick={() => marcar(horario)}
                  >
                    {formatarHora(horario.hora_inicio)}
                  </button>
                ))}
              </div>
            ) : (
              <AvisoVazio>
                {disponibilidade.motivo ?? "O estúdio não atende nesse dia."}
              </AvisoVazio>
            )
          ) : null}

          <p className="legenda">
            Cada horário ocupa uma hora. Os blocos apagados já estão ocupados ou
            já passaram.
          </p>
        </div>
      ) : null}

      {podeGerenciarEstaAgenda && !podeAgendar ? (
        <p className="legenda">
          A agenda abre depois do desenho aprovado e fecha quando a tatuagem é
          finalizada.
        </p>
      ) : null}

      {!podeGerenciarEstaAgenda ? (
        <p className="legenda">
          A agenda é organizada pelo tatuador responsável.
        </p>
      ) : null}
    </section>
  );
}
