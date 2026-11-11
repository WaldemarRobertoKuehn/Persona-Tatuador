"""Teste manual do fallback com uma entrada fictícia e um modelo Gemini inexistente."""


# Fazer uma chamada real apenas quando o arquivo for executado diretamente.
def testar_fallback() -> None:
    """Conferir qual reserva responde depois da falha do modelo principal."""
    from jangada_ai import LLM
    from jangada_ai.errors import LLMError

    # Reutilizar as reservas configuradas pelo projeto sem ler ou exibir chaves.
    from ia.modelos import claude, openrouter

    # Usar um nome fictício inexistente para provocar a troca do Gemini às reservas.
    gemini_inexistente = LLM("gemini", "modelo-inexistente-para-teste")
    llm_de_teste = gemini_inexistente.with_fallback(openrouter, claude)

    # Enviar somente texto fictício e mostrar apenas o provedor e o modelo que responderem.
    try:
        resposta = llm_de_teste.complete(
            "Responda somente com a frase: teste fictício de fallback."
        )
    except LLMError as erro:
        # Exibir o tipo da falha e o provedor, sem imprimir a mensagem que poderia
        # conter detalhes da requisição ou de configuração.
        provedor = erro.provider or "não identificado"
        print(
            "Nenhum provedor respondeu. "
            f"Último provedor: {provedor}; falha: {type(erro).__name__}."
        )
        raise SystemExit(1) from erro

    print(f"Reserva que respondeu: {resposta.provider}/{resposta.model}")


# Evitar qualquer chamada de rede ao importar o módulo para outros usos.
if __name__ == "__main__":
    testar_fallback()
