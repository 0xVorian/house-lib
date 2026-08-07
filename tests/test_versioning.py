from __future__ import annotations

import re
from pathlib import Path

import house_lib
from house_lib.versioning import build_info, read_git_sha, read_version

ROOT = Path(__file__).resolve().parents[1]


def test_packaged_versions_agree() -> None:
    """VERSION, pyproject.toml, and house_lib.__version__ must stay in sync."""
    file_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', pyproject)
    assert match is not None, "pyproject.toml missing project version"
    assert file_version == match.group(1) == house_lib.__version__


def test_read_version_from_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("APP_VERSION", raising=False)
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n", encoding="utf-8")
    assert read_version(version_file=version_file) == "1.2.3"


def test_build_info_includes_git_sha(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.setenv("GIT_SHA", "abcdefghijklmno")
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.1.0\n", encoding="utf-8")
    info = build_info("demo", version_file=version_file, cache=False)
    assert info == {
        "service": "demo",
        "version": "0.1.0",
        "git_sha": "abcdefghijkl",
    }
    assert read_git_sha() == "abcdefghijkl"
