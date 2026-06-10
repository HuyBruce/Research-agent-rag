from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path | None = None) -> None:
    """Load simple KEY=VALUE lines from .env without adding a dependency."""
    env_path = path or Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in {
            "LLM_PROVIDER",
            "GEMINI_MODEL",
            "HF_MODEL",
            "HF_MAX_NEW_TOKENS",
            "HF_TEMPERATURE",
            "OLLAMA_MODEL",
            "DISABLE_OLLAMA",
            "ALLOW_LOCAL_FALLBACK",
            "ENABLE_WEB_SEARCH",
            "WEB_SEARCH_PROVIDER",
            "WEB_SEARCH_LIMIT",
        }:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)
