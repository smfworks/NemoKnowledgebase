"""Client for SMF Nemotron-3-Embed-8B on Spark (OpenAI /v1/embeddings + /v2/embed)."""
from __future__ import annotations

import os
import time
from typing import Any, Iterable, Sequence

import numpy as np
import requests
from openai import OpenAI

DEFAULT_BASE = os.environ.get("NEMO_EMBED_BASE", "http://127.0.0.1:18001")
DEFAULT_MODEL = os.environ.get("NEMO_EMBED_MODEL", "nvidia/Nemotron-3-Embed-8B-BF16")
RECIPE_ID = "SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16"


def ensure_base(base: str) -> str:
    return base.rstrip("/")


def wait_ready(base: str, attempts: int = 60, sleep_s: float = 2.0) -> dict:
    base = ensure_base(base)
    last = None
    for i in range(1, attempts + 1):
        try:
            r = requests.get(f"{base}/v1/models", timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(sleep_s)
    raise RuntimeError(f"embed server not ready at {base}: {last}")


def l2_normalize(x: np.ndarray, axis: int = -1, eps: float = 1e-12) -> np.ndarray:
    n = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.maximum(n, eps)


class SparkEmbedClient:
    """Thin HTTP client for Praxis / bench scripts."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE,
        model: str = DEFAULT_MODEL,
        timeout: float = 300.0,
        use_v2: bool = True,
    ):
        self.base_url = ensure_base(base_url)
        self.model = model
        self.timeout = timeout
        self.use_v2 = use_v2
        self._oa = OpenAI(base_url=f"{self.base_url}/v1", api_key="EMPTY")

    def embed_v1(self, texts: Sequence[str], prefix: str | None = None) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        inputs = [f"{prefix}{t}" if prefix else t for t in texts]
        resp = self._oa.embeddings.create(
            model=self.model,
            input=list(inputs),
            encoding_format="float",
        )
        data = sorted(resp.data, key=lambda d: d.index)
        return np.array([d.embedding for d in data], dtype=np.float32)

    def embed_v2(self, texts: Sequence[str], input_type: str) -> np.ndarray:
        """input_type: query | document — server applies saved prompts."""
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        r = requests.post(
            f"{self.base_url}/v2/embed",
            json={
                "model": self.model,
                "input_type": input_type,
                "texts": list(texts),
                "embedding_types": ["float"],
                "truncate": "END",
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        payload = r.json()
        embs = payload.get("embeddings", {}).get("float")
        if embs is None:
            raise RuntimeError(f"unexpected /v2/embed response keys: {list(payload)}")
        return np.array(embs, dtype=np.float32)

    def embed_queries(self, texts: Sequence[str]) -> np.ndarray:
        if self.use_v2:
            try:
                return self.embed_v2(texts, "query")
            except Exception:
                return self.embed_v1(texts, "query: ")
        return self.embed_v1(texts, "query: ")

    def embed_documents(self, texts: Sequence[str]) -> np.ndarray:
        if self.use_v2:
            try:
                return self.embed_v2(texts, "document")
            except Exception:
                return self.embed_v1(texts, "passage: ")
        return self.embed_v1(texts, "passage: ")

    def embed_batched(
        self,
        texts: Sequence[str],
        *,
        kind: str,
        batch_size: int = 16,
    ) -> np.ndarray:
        """kind: query | document"""
        parts = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            if kind == "query":
                parts.append(self.embed_queries(chunk))
            else:
                parts.append(self.embed_documents(chunk))
        if not parts:
            return np.zeros((0, 0), dtype=np.float32)
        return np.vstack(parts)
