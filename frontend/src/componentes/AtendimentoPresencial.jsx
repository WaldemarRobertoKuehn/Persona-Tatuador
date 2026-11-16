/* O atendimento presencial: a cliente chega sem conta, o administrador cadastra
 * o nome dela, cria o pedido, pede uma proposta de desenho à IA e revisa o
 * resultado no mesmo lugar. A aprovação em si fica no bloco de imagens, que é a
 * tela que já mostra o desenho grande e registra o passo.
 */

import { useEffect, useState } from "react";

import {
  buscarClientes,
  cadastrarCliente,
  criarTatuagem,
  gerarDesenhoIA,
} from "../api";
import { AvisoCarregando, AvisoErro, AvisoVazio } from "./Avisos";
import Etiqueta from "./Etiqueta";
import ImagensDaTatuagem from "./ImagensDaTatuagem";

const PEDIDO_VAZIO = {
  cliente_id: "",
  tatuador_id: "",
  ideia: "",
  local_do_corpo: "",
  tamanho: "",
};

const ROTULO_DO_DESENHO = {
  pendente: "Aguardando revisão",
  aprovada: "Aprovado",
  recusada: "Recusado",
};

export default function AtendimentoPresencial({
  perfil,
  tatuadores,
  tatuagens,
  aoAtualizarTatuagens,
}) {
  const [clientes, setClientes] = useState([]);
  const [estadoClientes, setEstadoClientes] = useState("carregando");
  const [erroClientes, setErroClientes] = useState("");

  const [pedido, setPedido] = useState(PEDIDO_VAZIO);
  const [nomeDaCliente, setNomeDaCliente] = useState("");
  const [cadastrando, setCadastrando] = useState(false);
  const [criando, setCriando] = useState(false);
  const [gerandoId, setGerandoId] = useState(null);
  const [revisandoId, setRevisandoId] = useState(null);
  const [erro, setErro] = useState("");
  const [aviso, setAviso] = useState("");

  const presenciais = tatuagens.filter(
    (tatuagem) => tatuagem.origem === "presencial",
  );
  const tatuagemEmRevisao = presenciais.find(
    (tatuagem) => tatuagem.id === revisandoId,
  );

  function carregarClientes() {
    return buscarClientes()
      .then((recebidas) => {
        setClientes(recebidas);
        setEstadoClientes("pronto");
        setErroClientes("");
      })
      .catch((erroRecebido) => {
        setErroClientes(erroRecebido.message);
        setEstadoClientes("erro");
      });
  }

  useEffect(() => {
    carregarClientes();
  }, []);

  function mudar(campo, valor) {
    setPedido((anterior) => ({ ...anterior, [campo]: valor }));
  }

  function cadastrar(evento) {
    evento.preventDefault();
    setCadastrando(true);
    setErro("");
    setAviso("");

    cadastrarCliente(nomeDaCliente)
      .then((cliente) => {
        setNomeDaCliente("");
        setAviso(`${cliente.nome} está pronta para receber um pedido.`);
        setPedido((anterior) => ({
          ...anterior,
          cliente_id: String(cliente.id),
        }));
        return carregarClientes();
      })
      .catch((erroRecebido) => setErro(erroRecebido.message))
      .finally(() => setCadastrando(false));
  }

  function enviarPedido(evento) {
    evento.preventDefault();
    setCriando(true);
    setErro("");
    setAviso("");

    const dados = {
      cliente_id: Number(pedido.cliente_id),
      tatuador_id: pedido.tatuador_id
        ? Number(pedido.tatuador_id)
        : null,
      ideia: pedido.ideia,
      local_do_corpo: pedido.local_do_corpo,
      tamanho: Number(pedido.tamanho),
      origem: "presencial",
    };

    criarTatuagem(dados)
      .then((nova) => {
        setPedido(PEDIDO_VAZIO);
        setAviso(`Pedido #${nova.id} criado. Pedindo uma proposta de desenho à IA...`);

        return gerarDesenhoIA(nova.id)
          .then(() => {
            setAviso(
              `Pedido #${nova.id} criado e desenho gerado. ` +
                "Abra a revisão abaixo para aprovar ou recusar.",
            );
          })
          .catch((erroRecebido) => {
            setAviso(
              `Pedido #${nova.id} criado, mas a IA não gerou o desenho: ` +
                `${erroRecebido.message} Tente gerar novamente na lista abaixo.`,
            );
          })
          .then(() => aoAtualizarTatuagens());
      })
      .catch((erroRecebido) => setErro(erroRecebido.message))
      .finally(() => setCriando(false));
  }

  function gerarNovamente(tatuagem) {
    setGerandoId(tatuagem.id);
    setErro("");
    setAviso("");

    gerarDesenhoIA(tatuagem.id)
      .then(() => {
        setAviso(
          `Nova proposta do pedido #${tatuagem.id} pronta para revisão.`,
        );
        return aoAtualizarTatuagens();
      })
      .catch((erroRecebido) => setErro(erroRecebido.message))
      .finally(() => setGerandoId(null));
  }

  return (
    <section className="cartao">
      <h2>Atendimento presencial</h2>
      <p className="legenda legenda-folgada">
        Para a cliente que chegou no estúdio sem conta no site. Cadastre o nome,
        registre o pedido e peça uma proposta de desenho. A aprovação do desenho
        é registrada em nome da cliente e coloca a tatuagem na agenda do
        tatuador escolhido.
      </p>

      <form className="formulario-de-equipe" onSubmit={cadastrar}>
        <h4>1. Cadastrar a cliente</h4>
        <label className="campo">
          <span>Nome da cliente</span>
          <input
            value={nomeDaCliente}
            onChange={(evento) => setNomeDaCliente(evento.target.value)}
            minLength={2}
            maxLength={100}
            placeholder="Como a cliente quer ser chamada"
            required
          />
        </label>
        <button type="submit" className="botao-neutro" disabled={cadastrando}>
          {cadastrando ? "Cadastrando..." : "Cadastrar cliente"}
        </button>
      </form>

      {estadoClientes === "carregando" ? (
        <AvisoCarregando oQue="as clientes" />
      ) : null}
      {estadoClientes === "erro" ? <AvisoErro erro={erroClientes} /> : null}

      <form className="formulario-de-equipe" onSubmit={enviarPedido}>
        <h4>2. Registrar o pedido e gerar o desenho</h4>

        <label className="campo">
          <span>Cliente</span>
          <select
            value={pedido.cliente_id}
            onChange={(evento) => mudar("cliente_id", evento.target.value)}
            required
          >
            <option value="">Escolha a cliente</option>
            {clientes.map((cliente) => (
              <option key={cliente.id} value={cliente.id}>
                {cliente.nome}
              </option>
            ))}
          </select>
        </label>

        <label className="campo">
          <span>Ideia da tatuagem</span>
          <textarea
            value={pedido.ideia}
            onChange={(evento) => mudar("ideia", evento.target.value)}
            minLength={2}
            maxLength={1000}
            required
          />
        </label>

        <div className="par">
          <label className="campo">
            <span>Local do corpo</span>
            <input
              value={pedido.local_do_corpo}
              onChange={(evento) => mudar("local_do_corpo", evento.target.value)}
              minLength={2}
              maxLength={100}
              required
            />
          </label>

          <label className="campo">
            <span>Tamanho (cm)</span>
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={pedido.tamanho}
              onChange={(evento) => mudar("tamanho", evento.target.value)}
              required
            />
          </label>
        </div>

        <label className="campo">
          <span>Tatuador responsável (opcional)</span>
          <select
            value={pedido.tatuador_id}
            onChange={(evento) => mudar("tatuador_id", evento.target.value)}
          >
            <option value="">Usar o tatuador padrão</option>
            {tatuadores.map((tatuador) => (
              <option key={tatuador.id} value={tatuador.id}>
                {tatuador.nome}
              </option>
            ))}
          </select>
        </label>

        {erro ? (
          <p className="mensagem-erro" role="alert">
            {erro}
          </p>
        ) : null}
        {aviso ? (
          <p className="confirmacao" role="status">
            {aviso}
          </p>
        ) : null}

        <button
          type="submit"
          className="botao"
          disabled={criando || clientes.length === 0}
        >
          {criando ? "Criando pedido e desenhando..." : "Criar pedido e gerar desenho"}
        </button>
      </form>

      <h4>3. Revisar e aprovar</h4>

      {presenciais.length === 0 ? (
        <AvisoVazio>Nenhum pedido presencial registrado ainda.</AvisoVazio>
      ) : (
        <table className="tabela">
          <thead>
            <tr>
              <th scope="col">Pedido</th>
              <th scope="col">Cliente</th>
              <th scope="col">Desenho</th>
              <th scope="col">Etapa</th>
              <th scope="col">Tatuador</th>
              <th scope="col">Ação</th>
            </tr>
          </thead>
          <tbody>
            {presenciais.map((tatuagem) => (
              <tr key={tatuagem.id}>
                <td data-rotulo="Pedido">
                  #{tatuagem.id} · {tatuagem.ideia}
                </td>
                <td data-rotulo="Cliente">{tatuagem.nome_da_cliente}</td>
                <td data-rotulo="Desenho">
                  {tatuagem.desenho_status
                    ? ROTULO_DO_DESENHO[tatuagem.desenho_status] ??
                      tatuagem.desenho_status
                    : "Sem desenho"}
                </td>
                <td data-rotulo="Etapa">
                  <Etiqueta etapa={tatuagem.etapa} />
                </td>
                <td data-rotulo="Tatuador">
                  {tatuagem.tatuador_nome ?? "Sem tatuador"}
                </td>
                <td data-rotulo="Ação">
                  <div className="linha-de-botoes">
                    <button
                      type="button"
                      className="botao-neutro"
                      onClick={() =>
                        setRevisandoId(
                          revisandoId === tatuagem.id ? null : tatuagem.id,
                        )
                      }
                    >
                      {revisandoId === tatuagem.id
                        ? "Fechar revisão"
                        : "Revisar desenho"}
                    </button>
                    {tatuagem.desenho_status !== "aprovada" ? (
                      <button
                        type="button"
                        className="botao-neutro"
                        disabled={gerandoId !== null}
                        onClick={() => gerarNovamente(tatuagem)}
                      >
                        {gerandoId === tatuagem.id
                          ? "Gerando..."
                          : tatuagem.desenho_status
                            ? "Gerar outra proposta"
                            : "Gerar desenho"}
                      </button>
                    ) : null}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {revisandoId !== null ? (
        <div className="revisao-do-desenho">
          <ImagensDaTatuagem
            tatuagemId={revisandoId}
            ideia={tatuagemEmRevisao?.ideia ?? ""}
            origem={tatuagemEmRevisao?.origem ?? ""}
            perfil={perfil}
            aoAtualizarTatuagem={aoAtualizarTatuagens}
          />
        </div>
      ) : null}
    </section>
  );
}
