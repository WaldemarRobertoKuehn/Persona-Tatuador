"""Testar a ordem dos modelos sem carregar configuração nem chamar provedores."""

import importlib
import sys
import types


# Garantir que o fallback aponta primeiro ao OpenRouter e depois ao Claude.
def test_modelos_configuram_fallback_na_ordem_escolhida(monkeypatch):
    chamadas = []

    # Substituir LLM por um objeto falso que registra a ordem sem usar credenciais.
    class LLMFalso:
        def __init__(self, provedor, modelo):
            self.provedor = provedor
            self.modelo = modelo
            chamadas.append((provedor, modelo))

        def with_fallback(self, *reservas):
            return (self, *reservas)

    jangada_falsa = types.ModuleType("jangada_ai")
    jangada_falsa.LLM = LLMFalso
    configuracao_falsa = types.ModuleType("configuracao")

    # Substituir módulos externos antes de importar a configuração de provedores.
    monkeypatch.setitem(sys.modules, "jangada_ai", jangada_falsa)
    monkeypatch.setitem(sys.modules, "configuracao", configuracao_falsa)
    modulo_anterior = sys.modules.pop("ia.modelos", None)

    try:
        modelos = importlib.import_module("ia.modelos")

        # Conferir os nomes escolhidos e a composição exata da cadeia.
        assert chamadas == [
            ("gemini", "gemini-3.8-flash"),
            ("openrouter", "openrouter/free"),
            ("anthropic", "claude-opus-5-5"),
        ]
        assert modelos.llm == (
            modelos.gemini,
            modelos.openrouter,
            modelos.claude,
        )
    finally:
        # Restaurar o módulo real anterior para não afetar outros testes.
        sys.modules.pop("ia.modelos", None)
        if modulo_anterior is not None:
            sys.modules["ia.modelos"] = modulo_anterior
