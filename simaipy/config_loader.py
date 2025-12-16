from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Mapping

import yaml
from dotenv import load_dotenv
from pydantic import ValidationError

from .config_model import SimaipySettings

DEFAULT_CONFIG_DIR = Path("configs")


def load_yaml_config(path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML file.

    Raises FileNotFoundError if the file does not exist.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(
            f"YAML config at {path} must contain a mapping at the top level."
        )

    return dict(data)


def load_env_config(prefix: str = "SIMAI_") -> Dict[str, Any]:
    """Load configuration overrides from environment variables.

    The prefix is currently unused but kept for future extensibility.
    """
    mapping: Dict[str, str] = {
        "SIMAI_ENV": "env",
        "SIMAI_BASE_URL": "base_url",
        "SIMAI_TIMEOUT_SECONDS": "timeout_seconds",
        "SIMAI_USER_EMAIL": "user_email",
        "SIMAI_USER_PASSWORD": "user_password",
        "SIMAI_SEMANTIC_POS_THRESHOLD": "semantic_pos_threshold",
        "SIMAI_SEMANTIC_NEG_THRESHOLD": "semantic_neg_threshold",
    }

    result: Dict[str, Any] = {}
    for env_name, field_name in mapping.items():
        if env_name in os.environ:
            result[field_name] = os.environ[env_name]
    return result


def resolve_env_for_profile(cli_env: str | None = None) -> str | None:
    """Determine which environment profile to use for YAML selection.

    Order:
    - CLI `--env`
    - `SIMAI_ENV` (from real env or .env)

    Returns None if no environment is specified (no defaults).
    """
    if cli_env:
        return cli_env
    env_from_os = os.getenv("SIMAI_ENV")
    if env_from_os:
        return env_from_os
    return None


def _coerce_types(raw: Mapping[str, Any]) -> Dict[str, Any]:
    """Perform light type coercion before validation where it helps.

    Pydantic will also coerce, but we keep this as a convenient hook.
    """
    coerced: Dict[str, Any] = dict(raw)
    if "timeout_seconds" in coerced and isinstance(coerced["timeout_seconds"], str):
        try:
            coerced["timeout_seconds"] = int(coerced["timeout_seconds"])
        except ValueError:
            # Let pydantic produce a nice validation error later.
            pass
    return coerced


def merge_configs(
    yaml_cfg: Mapping[str, Any],
    env_cfg: Mapping[str, Any],
    cli_cfg: Mapping[str, Any],
) -> SimaipySettings:
    """Merge configuration layers respecting precedence.

    Precedence (highest last): YAML < env < CLI.
    """
    merged: Dict[str, Any] = {}
    merged.update(yaml_cfg)
    merged.update(env_cfg)
    merged.update({k: v for k, v in cli_cfg.items() if v is not None})

    merged = _coerce_types(merged)

    try:
        return SimaipySettings(**merged)
    except ValidationError as exc:
        raise ValueError(f"Invalid configuration: {exc}") from exc


def build_settings(
    yaml_path: Path | None = None,
    env_prefix: str = "SIMAI_",
    cli_options: Mapping[str, Any] | None = None,
) -> SimaipySettings:
    """Build a `SimaipySettings` instance from YAML, env, and CLI options.

    Configuration must be provided via CLI, environment variables, or config file.
    No defaults are used - all values must be explicitly provided.
    """
    # Load values from .env into os.environ (if file exists)
    load_dotenv()

    cli_cfg = dict(cli_options or {})

    # Decide which profile YAML to load if caller didn't pass an explicit path.
    resolved_yaml_path = yaml_path
    if resolved_yaml_path is None:
        profile_env = resolve_env_for_profile(cli_cfg.get("env"))
        if profile_env is None:
            raise ValueError(
                "No configuration file path provided and no environment specified. "
                "Either provide --config PATH, --env ENV_NAME, or set SIMAI_ENV environment variable."
            )
        resolved_yaml_path = DEFAULT_CONFIG_DIR / f"{profile_env}.yaml"

    yaml_cfg = load_yaml_config(resolved_yaml_path)
    # Note: env_prefix is reserved for future use when we add more flexible mapping.
    _ = env_prefix
    env_cfg = load_env_config()
    return merge_configs(yaml_cfg, env_cfg, cli_cfg)


__all__ = [
    "DEFAULT_CONFIG_DIR",
    "load_yaml_config",
    "load_env_config",
    "resolve_env_for_profile",
    "merge_configs",
    "build_settings",
]
