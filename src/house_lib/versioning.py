"""Standard service version / git SHA helpers for /health."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any


def read_git_sha() -> str | None:
    value = os.environ.get("GIT_SHA", "").strip()
    if not value or value == "unknown":
        return None
    return value[:12]


def read_version(*, version_file: Path | None = None, env_var: str = "APP_VERSION") -> str:
    env_version = os.environ.get(env_var)
    if env_version:
        return env_version.strip()

    if version_file is not None and version_file.is_file():
        return version_file.read_text(encoding="utf-8").strip()

    return "0.0.0"


@lru_cache(maxsize=8)
def _cached_version(version_file_str: str) -> str:
    return read_version(version_file=Path(version_file_str))


def build_info(
    service: str,
    *,
    version_file: Path | None = None,
    cache: bool = True,
) -> dict[str, Any]:
    if version_file is not None and cache:
        version = _cached_version(str(version_file.resolve()))
    else:
        version = read_version(version_file=version_file)

    info: dict[str, Any] = {
        "service": service,
        "version": version,
    }
    git_sha = read_git_sha()
    if git_sha:
        info["git_sha"] = git_sha
    return info
