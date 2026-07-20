"""MTEB EncoderProtocol wrapper for remote Spark Nemotron-3-Embed OpenAI API."""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

import numpy as np
from openai import OpenAI

from mteb.models.abs_encoder import AbsEncoder
from mteb.models.model_meta import ModelMeta, ScoringFunction
from mteb.types import PromptType

if TYPE_CHECKING:
    from torch.utils.data import DataLoader

    from mteb.abstasks.task_metadata import TaskMetadata
    from mteb.types import Array, BatchedInput

logger = logging.getLogger(__name__)


def _build_meta(model_name: str, embed_dim: int, max_tokens: int) -> ModelMeta:
    """ModelMeta requires a loader callable; for remote-serve we load self externally."""

    def _loader(**_kwargs: Any) -> SparkNemotron3EmbedEncoder:
        raise RuntimeError(
            "Use SparkNemotron3EmbedEncoder(...) directly; remote serve is already running"
        )

    return ModelMeta(
        loader=_loader,
        name=model_name if "/" in model_name else f"nvidia/{model_name}",
        revision="spark-served",
        release_date="2026-07-16",
        languages=["eng-Latn"],
        n_parameters=8_000_000_000,
        memory_usage_mb=15_000.0,
        max_tokens=float(max_tokens),
        embed_dim=embed_dim,
        license="not specified",  # OpenMDW-1.1 not in enum
        open_weights=True,
        public_training_code=None,
        public_training_data=None,
        framework=["PyTorch", "Sentence Transformers", "API"],
        reference="https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16",
        similarity_fn_name=ScoringFunction.COSINE,
        use_instructions=True,
        training_datasets=None,
    )


class SparkNemotron3EmbedEncoder(AbsEncoder):
    """Encode via vLLM OpenAI-compatible /v1/embeddings with Nemotron query/passage prefixes.

    NVIDIA card requires:
      - queries:   prefix ``query: ``
      - documents: prefix ``passage: ``

    Long BEIR/RTEB docs (e.g. TRECCOVID) are truncated to ``max_seq_len`` tokens so they
    fit the live serve ``--max-model-len`` (default 8192). NVIDIA card eval used 4096;
    override with max_seq_len=4096 for closer parity.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:18001/v1",
        model_name: str = "nvidia/Nemotron-3-Embed-8B-BF16",
        embed_dim: int = 4096,
        batch_size: int = 16,
        query_prefix: str = "query: ",
        document_prefix: str = "passage: ",
        max_retries: int = 5,
        max_seq_len: int = 8192,
        tokenizer_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/v1"):
            if self.base_url.endswith("/v1/"):
                self.base_url = self.base_url.rstrip("/")
            elif "/v1" not in self.base_url:
                self.base_url = f"{self.base_url}/v1"
        self.model_name = model_name
        self._embed_dim = embed_dim
        self.batch_size = batch_size
        self.query_prefix = query_prefix
        self.document_prefix = document_prefix
        self.max_retries = max_retries
        # leave 8 tokens headroom for tokenizer/server mismatch
        self.max_seq_len = max(64, int(max_seq_len) - 8)
        self._client = OpenAI(base_url=self.base_url, api_key="EMPTY", timeout=600.0)
        self.mteb_model_meta = _build_meta(model_name, embed_dim, max_seq_len)

        tok_id = tokenizer_id or model_name
        try:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(
                tok_id, trust_remote_code=True
            )
            logger.info("Loaded tokenizer %s for truncation max_seq_len=%s", tok_id, self.max_seq_len)
        except Exception as e:  # noqa: BLE001
            logger.warning("Tokenizer load failed (%s); using char budget fallback", e)
            self._tokenizer = None

    def _prefix_for(self, prompt_type: PromptType | None) -> str:
        if prompt_type == PromptType.query:
            return self.query_prefix
        if prompt_type == PromptType.document:
            return self.document_prefix
        return self.document_prefix

    def _truncate_with_prefix(self, text: str, prefix: str) -> str:
        """Ensure prefix+text fits in max_seq_len tokens (server limit)."""
        text = text if text is not None else ""
        if self._tokenizer is None:
            # ~3 chars/token rough; keep prefix
            budget = max(0, self.max_seq_len * 3 - len(prefix))
            return f"{prefix}{text[:budget]}"

        # Tokenize body only; reserve space for prefix + specials
        prefix_ids = self._tokenizer.encode(prefix, add_special_tokens=False)
        specials = 2  # bos/eos style headroom
        body_budget = max(0, self.max_seq_len - len(prefix_ids) - specials)
        body_ids = self._tokenizer.encode(text, add_special_tokens=False)
        if len(body_ids) > body_budget:
            body_ids = body_ids[:body_budget]
            text = self._tokenizer.decode(body_ids, skip_special_tokens=True)
        return f"{prefix}{text}"

    def encode(
        self,
        inputs: DataLoader[BatchedInput],
        *,
        task_metadata: TaskMetadata,
        hf_split: str,
        hf_subset: str,
        prompt_type: PromptType | None = None,
        **kwargs: Any,
    ) -> Array:
        sentences = [text for batch in inputs for text in batch["text"]]
        prefix = self._prefix_for(prompt_type)
        batch_size = int(kwargs.get("batch_size", self.batch_size))

        all_embs: list[np.ndarray] = []
        for i in range(0, len(sentences), batch_size):
            chunk = sentences[i : i + batch_size]
            non_empty_idx = [j for j, t in enumerate(chunk) if t and str(t).strip()]
            out = np.zeros((len(chunk), self._embed_dim), dtype=np.float32)
            if non_empty_idx:
                payload = [
                    self._truncate_with_prefix(str(chunk[j]), prefix) for j in non_empty_idx
                ]
                last_err = None
                # On 400 context errors, shrink further and retry
                for attempt in range(self.max_retries):
                    try:
                        resp = self._client.embeddings.create(
                            model=self.model_name,
                            input=payload,
                            encoding_format="float",
                        )
                        data = sorted(resp.data, key=lambda d: d.index)
                        embs = np.array([d.embedding for d in data], dtype=np.float32)
                        if embs.shape[1] != self._embed_dim:
                            self._embed_dim = embs.shape[1]
                            if out.shape[1] != self._embed_dim:
                                out = np.zeros(
                                    (len(chunk), self._embed_dim), dtype=np.float32
                                )
                        for k, j in enumerate(non_empty_idx):
                            out[j] = embs[k]
                        last_err = None
                        break
                    except Exception as e:  # noqa: BLE001
                        last_err = e
                        msg = str(e)
                        if "maximum context length" in msg or "input_tokens" in msg:
                            # emergency hard char cut (handles tokenizer/server mismatch)
                            cut = max(256, int(len(payload[0]) * 0.85)) if payload else 256
                            payload = [p[:cut] for p in payload]
                            logger.warning(
                                "Context overflow; hard-truncating batch to %s chars (attempt %s)",
                                cut,
                                attempt + 1,
                            )
                        time.sleep(min(2**attempt, 30))
                if last_err is not None:
                    raise last_err
            all_embs.append(out)

        if not all_embs:
            return np.zeros((0, self._embed_dim), dtype=np.float32)
        return np.vstack(all_embs)
