"""Configurar os provedores de linguagem usados pela funcionalidade."""

from jangada_ai import LLM

# Carregar a configuração central para disponibilizar as variáveis do ambiente
# ao Jangada, sem copiar ou exibir valores de credenciais neste módulo.
import configuracao

# Configurar o Gemini principal usando o modelo adotado nas regras da aula.
gemini = LLM("gemini", "gemini-3.8-flash")

# Configurar a primeira reserva gratuita, deixando o OpenRouter escolher o modelo.
openrouter = LLM("openrouter", "openrouter/free")

# Configurar o Claude pago como terceira opção, após Gemini e OpenRouter falharem.
claude = LLM("anthropic", "claude-opus-5-5")

# Encadear os provedores na ordem de prioridade escolhida para a funcionalidade.
llm = gemini.with_fallback(openrouter, claude)
