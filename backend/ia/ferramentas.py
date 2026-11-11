"""Tools de leitura para a funcionalidade de resumo do histórico."""

import json
from collections.abc import Callable

# Reutilizar o serviço existente para ler a linha do tempo sem duplicar consultas
# ao banco nem tocar na regra que registra passos.
import servicos.passo as servico_passos


# Vincular a consulta ao registro que a rota já autorizou, sem expor ao modelo
# um argumento de tatuagem que pudesse ser trocado durante a chamada da tool.
def criar_ferramenta_historico(tatuagem: dict) -> Callable[[], str]:
    """Criar uma consulta sem argumentos, limitada à tatuagem autorizada."""

    tatuagem_id = tatuagem["id"]
    etapa_atual = tatuagem["etapa"]

    # Consultar apenas os passos do id vinculado e devolver os campos necessários
    # ao resumo, sem nome, identificador de pessoa ou dado de autenticação.
    def consultar_historico_da_tatuagem() -> str:
        """Ler a etapa e os passos numerados da tatuagem autorizada."""
        passos = servico_passos.listar_passos(tatuagem_id)
        historico = {
            "etapa_atual": etapa_atual,
            "passos": [
                {
                    "numero": numero,
                    "tipo": passo["tipo"],
                    "data": passo["data"].isoformat(),
                    "observacao": passo["observacao"],
                }
                for numero, passo in enumerate(passos, start=1)
            ],
        }
        return json.dumps(historico, ensure_ascii=False)

    return consultar_historico_da_tatuagem


# Registrar a fábrica da tool para que a funcionalidade crie uma consulta
# vinculada à tatuagem autorizada de cada requisição.
FERRAMENTAS = [criar_ferramenta_historico]
