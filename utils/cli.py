from __future__ import annotations

import argparse

from .config import load_config
from .shell import parse_env_file, shell_quote


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Utilities for shell scripts and config files.")
    parser.add_argument("--quote", dest="quoted", help="Quote a string for shell use")
    parser.add_argument("--env-file", dest="env_file", help="Read a shell environment file and print KEY=VALUE pairs")
    parser.add_argument("--config", dest="config_file", help="Load a config file (JSON, INI, or env-style)")
    args = parser.parse_args(argv)

    if args.quoted is not None:
        print(shell_quote(args.quoted))
        return 0
    if args.env_file:
        for key, value in parse_env_file(args.env_file).items():
            print(f"{key}={value}")
        return 0
    if args.config_file:
        print(load_config(args.config_file))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
