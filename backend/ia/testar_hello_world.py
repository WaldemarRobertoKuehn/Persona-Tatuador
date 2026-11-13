"""Teste manual da cadeia de provedores de IA com uma mensagem fictícia."""

import sys
from pathlib import Path


CAMINHO_BACKEND = Path(__file__).resolve().parents[1]
if str(CAMINHO_BACKEND) not in sys.path:
    sys.path.insert(0, str(CAMINHO_BACKEND))


def testar_hello_world() -> None:
    """Fazer uma chamada simples e mostrar somente o resultado ou metadados da falha."""
    # Carregar primeiro a configuração da API, que usa o .env da raiz do projeto.
    import configuracao

    from jangada_ai.errors import LLMError

    from ia.modelos import llm

    try:
        resposta = llm.complete("Responda somente com: hello-world")
    except LLMError as erro:
        print(
            "Falha na cadeia de IA: "
            f"provedor={erro.provider or 'não identificado'} "
            f"categoria={erro.category} "
            f"status={erro.status_code or 'não informado'}"
        )
        raise SystemExit(1) from None

    print(f"Resposta: {resposta.text}")
    print(f"Provedor: {resposta.provider}")
    print(f"Modelo: {resposta.model}")


if __name__ == "__main__":
    testar_hello_world()
