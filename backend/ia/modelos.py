from jangada_ai import LLM
import configuracao
gemini = LLM("gemini", "gemini-3.5-flash-lite", api_key=configuracao.chave_do_gemini)
# a primeira reserva: um modelo grátis escolhido pelo OpenRouter
openrouter = LLM("openrouter", "openrouter/free",
                 api_key=configuracao.chave_do_openrouter)
# a terceira opção: o Claude, pago; só entra quando os outros falham
#claude = LLM("anthropic", "claude-opus-5-5", api_key=configuracao.chave_do_claude)
llm = gemini.with_fallback(openrouter)