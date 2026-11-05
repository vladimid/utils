from __future__ import annotations

import configparser
import json
from pathlib import Path
from typing import Any


def parse_ini(path: str | Path) -> dict[str, dict[str, str]]:
    """Parse a simple INI file into a nested dictionary."""
    parser = configparser.ConfigParser()
    parser.read(path)
    return {section: dict(parser[section]) for section in parser.sections()}


def load_config(path: str | Path, *, default: dict[str, Any] | None = None) -> Any:
    """Load JSON, INI, or shell-style environment configuration from a file."""
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    suffix = source.suffix.lower()

    if suffix == ".json":
        return json.loads(text)
    if suffix == ".ini":
        result = parse_ini(source)
        if default:
            for section, values in default.items():
                result.setdefault(section, {}).update(values)
        return result
    if text.lstrip().startswith("{") or text.lstrip().startswith("["):
        return json.loads(text)
    if "=" in text:
        return {**(default or {}), **_parse_simple_kv(text)}
    raise ValueError(f"Unsupported config format for {source}")


def _parse_simple_kv(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            continue
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def write_config(path: str | Path, data: Any, *, fmt: str | None = None) -> None:
    """Persist data to a JSON or INI-style configuration file."""
    source = Path(path)
    if fmt is None:
        fmt = source.suffix.lower().lstrip(".") or "json"

    if fmt == "json":
        source.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return
    if fmt == "ini":
        parser = configparser.ConfigParser()
        if isinstance(data, dict):
            for section, values in data.items():
                parser[section] = dict(values)
        else:
            raise TypeError("INI output requires a dict of section->key-value mappings")
        with source.open("w", encoding="utf-8") as handle:
            parser.write(handle)
        return
    raise ValueError(f"Unsupported config format: {fmt}")
