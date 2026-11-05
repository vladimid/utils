from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Mapping, Sequence


def shell_quote(value: object) -> str:
    """Return a POSIX-safe shell representation for a value."""
    return shlex.quote(str(value))


quote = shell_quote


def command_exists(command: str) -> bool:
    """Return True when a command is present on PATH."""
    return shutil.which(command) is not None


def run_command(
    command: str | Sequence[str],
    *,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    shell: bool = False,
    check: bool = False,
    capture_output: bool = True,
    text: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command while keeping a simple, test-friendly API."""
    if isinstance(command, str):
        argv = command if shell else shlex.split(command)
    else:
        argv = list(command)

    result = subprocess.run(
        argv,
        cwd=str(cwd) if cwd is not None else None,
        env=dict(os.environ, **(env or {})) if env is not None else None,
        shell=shell,
        check=check,
        capture_output=capture_output,
        text=text,
    )
    return result


def expand_vars(value: str, environment: Mapping[str, str] | None = None) -> str:
    """Expand environment variables and user-home shorthand in a string."""
    mapping = dict(os.environ)
    if environment:
        mapping.update(environment)
    expanded = os.path.expandvars(os.path.expanduser(value))
    return expanded.format_map(mapping)


def parse_env_file(path: str | os.PathLike[str], *, environment: Mapping[str, str] | None = None) -> dict[str, str]:
    """Parse a shell-style environment file, returning a dictionary of key-value pairs."""
    values: dict[str, str] = {}
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, _, value = line.partition("=")
        if not _:
            continue
        key = key.strip()
        value = value.strip()
        if value and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = expand_vars(value, environment)
    return values
