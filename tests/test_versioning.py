from __future__ import annotations

from pathlib import Path

from house_lib.versioning import build_info, read_git_sha, read_version


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
