from __future__ import annotations

import os
from typing import Any, Optional

from sentence_transformers import SentenceTransformer, util

_MODEL: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    """Lazily load a local Hugging Face sentence-transformer model.

    Model must be specified via SIMAI_SEMANTIC_MODEL environment variable.
    Examples:
    - sentence-transformers/all-MiniLM-L6-v2  (light and fast)
    - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (for better AR)
    """
    global _MODEL
    if _MODEL is None:
        model_name = os.getenv("SIMAI_SEMANTIC_MODEL")
        if not model_name:
            raise ValueError(
                "SIMAI_SEMANTIC_MODEL environment variable must be set. "
                "No default model is provided."
            )
        _MODEL = SentenceTransformer(model_name)
    return _MODEL


def _similarity(a: str, b: str) -> float:
    model = _get_model()
    emb = model.encode([a, b], convert_to_tensor=True)
    sim = util.cos_sim(emb[0], emb[1]).item()
    return float(sim)


def semantic_pass(
    reply: str,
    expectation: str,
    pos_threshold: float,
    neg_threshold: float,
    negative_expectation: Optional[str] = None,
) -> bool:
    """Return True if the reply semantically matches expectations using a local HF model.

    Logic (no keyword rules, only embeddings):
    - Compute cosine similarity between reply and expectation.
    - Optionally compute similarity between reply and negative_expectation.
    - Pass if:
        sim_pos >= pos_threshold
        and (negative is None or sim_neg <= neg_threshold).

    Args:
        reply: The actual reply text to evaluate.
        expectation: The expected reply text.
        pos_threshold: Positive semantic similarity threshold (must be provided).
        neg_threshold: Negative semantic similarity threshold (must be provided).
        negative_expectation: Optional negative expectation to check against.

    Thresholds must be provided via CLI, environment variables, or config files.
    No defaults are used.
    """
    sim_pos = _similarity(reply, expectation)

    if negative_expectation:
        sim_neg = _similarity(reply, negative_expectation)
    else:
        sim_neg = 0.0

    return sim_pos >= pos_threshold and (
        not negative_expectation or sim_neg <= neg_threshold
    )


def semantic_evaluate(
    reply: str,
    expectation: str,
    pos_threshold: float,
    neg_threshold: float,
    negative_expectation: Optional[str] = None,
) -> dict[str, Any]:
    """Evaluate semantic similarity and return detailed results.

    Returns a dictionary with:
    - passed: bool indicating if the test passed
    - similarity_score: float similarity score with expectation
    - negative_similarity_score: float similarity score with negative expectation (if provided)
    - pos_threshold: positive threshold used
    - neg_threshold: negative threshold used

    Args:
        reply: The actual reply text to evaluate.
        expectation: The expected reply text.
        pos_threshold: Positive semantic similarity threshold.
        neg_threshold: Negative semantic similarity threshold.
        negative_expectation: Optional negative expectation to check against.

    Returns:
        Dictionary with evaluation results.
    """
    sim_pos = _similarity(reply, expectation)

    if negative_expectation:
        sim_neg = _similarity(reply, negative_expectation)
    else:
        sim_neg = None

    passed = sim_pos >= pos_threshold and (
        not negative_expectation or (sim_neg is not None and sim_neg <= neg_threshold)
    )

    return {
        "passed": passed,
        "similarity_score": sim_pos,
        "negative_similarity_score": sim_neg,
        "pos_threshold": pos_threshold,
        "neg_threshold": neg_threshold,
    }


__all__ = ["semantic_pass", "semantic_evaluate"]
