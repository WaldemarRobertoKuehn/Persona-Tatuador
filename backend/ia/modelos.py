"""Configurar os provedores de linguagem usados pela funcionalidade."""

from jangada_ai import LLM
from jangada_ai.errors import AuthError, DEFAULT_FAILOVER

# Carregar a configuração central para disponibilizar as variáveis do ambiente
# ao Jangada, sem copiar ou exibir valores de credenciais neste módulo.
import configuracao

# Permitir a próxima opção da cadeia em falhas transitórias e de autenticação.
ERROS_DE_FALLBACK = (*DEFAULT_FAILOVER, AuthError)

# Configurar o Gemini como segunda opção sem repetir a mesma chamada.
# O modelo 3.5 é usado porque o 3.8 responde 503 de alta demanda com frequência.
# O timeout e a ausência de retentativa fazem a reserva assumir rapidamente em
# vez de deixar a pessoa esperando por uma resposta que não vem.
gemini = LLM(
    "gemini",
    "gemini-3.5-flash",
    retry_on=ERROS_DE_FALLBACK,
    max_retries=0,
    http_options={"timeout": 30000},
)

# Configurar o OpenRouter como provedor principal e deixar que escolha o modelo.
openrouter = LLM(
    "openrouter",
    "openrouter/free",
    retry_on=ERROS_DE_FALLBACK,
)

# Configurar o Claude pago como terceira opção, após OpenRouter e Gemini falharem.
claude = LLM("anthropic", "claude-opus-5-5")

# Encadear os provedores na ordem de prioridade escolhida para a funcionalidade.
llm = openrouter.with_fallback(gemini, claude)
