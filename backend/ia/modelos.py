"""Configurar os provedores de linguagem usados pela funcionalidade."""

from jangada_ai import LLM
from jangada_ai.errors import AuthError, DEFAULT_FAILOVER

# Carregar a configuração central para disponibilizar as variáveis do ambiente
# ao Jangada, sem copiar ou exibir valores de credenciais neste módulo.
import configuracao

# Configurar o Gemini principal e permitir a troca de provedor quando a
# credencial dele estiver ausente ou inválida, sem repetir a mesma chamada.
gemini = LLM(
    "gemini",
    "gemini-3.8-flash",
    retry_on=(*DEFAULT_FAILOVER, AuthError),
)

# Configurar a primeira reserva gratuita, deixando o OpenRouter escolher o modelo.
openrouter = LLM("openrouter", "openrouter/free")

# Configurar o Claude pago como terceira opção, após Gemini e OpenRouter falharem.
claude = LLM("anthropic", "claude-opus-5-5")

# Encadear os provedores na ordem de prioridade escolhida para a funcionalidade.
llm = gemini.with_fallback(openrouter, claude)
