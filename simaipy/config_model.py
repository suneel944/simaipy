from __future__ import annotations

from pydantic import BaseModel, Field


class SimaipySettings(BaseModel):
    """Configuration settings for simaipy.

    This model is intentionally small for now; you can extend it as needed.
    """

    env: str = Field(
        ...,
        description="Environment name (e.g. dev, stage, prod).",
    )
    base_url: str = Field(
        ...,
        description="Base URL for the application under test.",
    )
    timeout_seconds: int = Field(
        ...,
        description="Timeout in seconds for requests / operations.",
        ge=0,
    )
    semantic_pos_threshold: float = Field(
        ...,
        description="Threshold for positive semantic similarity.",
        ge=0.0,
        le=1.0,
    )
    semantic_neg_threshold: float = Field(
        ...,
        description="Threshold for negative semantic similarity.",
        ge=0.0,
        le=1.0,
    )
    user_email: str = Field(
        ...,
        description="Email address for the chatbot.",
    )
    user_password: str = Field(
        ...,
        description="Password for the chatbot.",
    )


__all__ = ["SimaipySettings"]
