from __future__ import annotations

import os


VALID_PROVIDERS = {"gemini", "ollama", "auto"}
VALID_FALLBACK_VALUES = {"0", "1"}
VALID_WEB_VALUES = {"0", "1"}


def get_status() -> dict[str, str]:
    return {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "gemini"),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3.2:1b"),
        "DISABLE_OLLAMA": os.getenv("DISABLE_OLLAMA", "1"),
        "ALLOW_LOCAL_FALLBACK": os.getenv("ALLOW_LOCAL_FALLBACK", "0"),
        "ENABLE_WEB_SEARCH": os.getenv("ENABLE_WEB_SEARCH", "1"),
        "WEB_SEARCH_PROVIDER": os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo"),
        "WEB_SEARCH_LIMIT": os.getenv("WEB_SEARCH_LIMIT", "5"),
    }


def set_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in VALID_PROVIDERS:
        return "Invalid provider. Use: gemini, ollama, or auto."

    os.environ["LLM_PROVIDER"] = normalized
    if normalized == "ollama":
        os.environ["DISABLE_OLLAMA"] = "0"
    elif normalized == "gemini":
        os.environ["DISABLE_OLLAMA"] = "1"
    return f"LLM_PROVIDER set to {normalized}."


def set_model(model: str) -> str:
    model = model.strip()
    if not model:
        return "Usage: /model <model-name>"

    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if provider == "ollama":
        os.environ["OLLAMA_MODEL"] = model
        return f"OLLAMA_MODEL set to {model}."

    os.environ["GEMINI_MODEL"] = model
    return f"GEMINI_MODEL set to {model}."


def set_fallback(value: str) -> str:
    normalized = _on_off_to_flag(value)
    if normalized not in VALID_FALLBACK_VALUES:
        return "Usage: /fallback on or /fallback off"
    os.environ["ALLOW_LOCAL_FALLBACK"] = normalized
    return f"ALLOW_LOCAL_FALLBACK set to {normalized}."


def set_web(value: str) -> str:
    normalized = _on_off_to_flag(value)
    if normalized not in VALID_WEB_VALUES:
        return "Usage: /web on or /web off"
    os.environ["ENABLE_WEB_SEARCH"] = normalized
    return f"ENABLE_WEB_SEARCH set to {normalized}."


def format_status() -> str:
    status = get_status()
    return "\n".join(f"- {key}: {value}" for key, value in status.items())


def _on_off_to_flag(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in {"on", "true", "yes", "1"}:
        return "1"
    if normalized in {"off", "false", "no", "0"}:
        return "0"
    return normalized
