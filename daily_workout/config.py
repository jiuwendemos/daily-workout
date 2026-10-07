"""Model and embedding configuration, read from the environment (.env)."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def make_model():
    """Build a ``Model`` from environment variables."""
    from openjiuwen.core.foundation.llm import (
        Model,
        ModelClientConfig,
        ModelRequestConfig,
    )

    client = ModelClientConfig(
        client_provider=os.getenv("MODEL_PROVIDER", "OpenAI"),
        api_key=os.getenv("API_KEY", ""),
        api_base=os.getenv("API_BASE", ""),
        timeout=int(os.getenv("LLM_TIMEOUT", "120")),
        verify_ssl=_bool("LLM_SSL_VERIFY", "false"),
    )
    request = ModelRequestConfig(
        model=os.getenv("MODEL_NAME", ""),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        top_p=0.9,
    )
    return Model(model_client_config=client, model_config=request)


def has_embedding() -> bool:
    return bool(os.getenv("EMBED_API_KEY")) and bool(os.getenv("EMBED_API_BASE"))


def embedding_config():
    """Build an ``EmbeddingConfig`` (only used when ``EMBED_*`` is set)."""
    from openjiuwen.core.foundation.store.base_embedding import EmbeddingConfig

    return EmbeddingConfig(
        model_name=os.getenv("EMBED_MODEL_NAME", "text-embedding-v3"),
        base_url=os.getenv("EMBED_API_BASE", ""),
        api_key=os.getenv("EMBED_API_KEY", ""),
    )


def validate() -> None:
    missing = [k for k in ("API_KEY", "API_BASE", "MODEL_NAME") if not os.getenv(k)]
    if missing:
        raise SystemExit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ".\nCopy .env.example to .env and fill it in."
        )
