from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from patchops.chatgpt_uploader.report_packager import build_safe_report_copy, safe_upload_name


def test_safe_upload_name_keeps_simple_txt_name() -> None:
    assert safe_upload_name(Path("patchops report.txt")) == "patchops_report.txt"


def test_build_safe_report_copy_creates_staged_copy(tmp_path: Path) -> None:
    source = tmp_path / "patchops report.txt"
    source_bytes = b"PatchOps report body\n"
    source.write_bytes(source_bytes)

    staging = tmp_path / "staging"
    candidate = build_safe_report_copy(source, staging_root=staging)

    staged = Path(candidate.staged_path)
    staged_bytes = staged.read_bytes()

    assert staged.exists()
    assert staged_bytes == source_bytes
    assert staged.read_text(encoding="utf-8") == "PatchOps report body\n"
    assert candidate.size_bytes == len(staged_bytes)
    assert candidate.size_bytes == staged.stat().st_size
    assert candidate.sha256 == hashlib.sha256(source_bytes).hexdigest()
    assert candidate.safe_name.endswith("_patchops_report.txt")


def test_build_safe_report_copy_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_safe_report_copy(tmp_path / "missing.txt", staging_root=tmp_path / "staging")


def test_build_safe_report_copy_rejects_unsupported_suffix(tmp_path: Path) -> None:
    source = tmp_path / "report.exe"
    source.write_bytes(b"nope")

    with pytest.raises(ValueError):
        build_safe_report_copy(source, staging_root=tmp_path / "staging")
