from __future__ import annotations

import argparse
from pathlib import Path

from .config_loader import build_settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the `simaipy` command."""
    parser = argparse.ArgumentParser(prog="simaipy")
    parser.add_argument(
        "--env",
        help="Environment name (dev/stage/prod).",
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        help="Base URL for the application under test.",
    )
    parser.add_argument(
        "--timeout",
        dest="timeout_seconds",
        type=int,
        help="Timeout in seconds for requests / operations.",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        type=Path,
        help="Path to YAML configuration file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Entry point for the `simaipy` CLI.

    For now we only build and print the resolved configuration, which
    demonstrates the precedence chain:
        CLI > env > YAML.

    Later we can wire this into the actual test runner / framework.
    """
    args = parse_args(argv)
    cli_cfg = {
        "env": args.env,
        "base_url": args.base_url,
        "timeout_seconds": args.timeout_seconds,
    }

    settings = build_settings(
        yaml_path=args.config_path,
        cli_options=cli_cfg,
    )

    # For now we simply echo the resolved settings; this is useful for debugging.
    # Replace this with your actual framework invocation.
    print(settings.model_dump_json(indent=2))  # noqa: T201


if __name__ == "__main__":
    main()
