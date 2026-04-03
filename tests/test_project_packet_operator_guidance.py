from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_workflow_doc_mentions_self_hosted_operator_flow() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "Patch 79 - self-hosted operator flow" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "Keep PowerShell thin" in text


def test_operator_quickstart_mentions_project_packet_commands() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "Patch 79 - project-packet operator commands" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "export-handoff" in text
    assert "one canonical report remains required" in text


def test_project_status_mentions_patch_79_and_patch_80() -> None:
    text = _read("docs/project_status.md")
    assert "Patch 79" in text
    assert "self-hosted operator guidance" in text
    assert "Patch 80" in text


def test_wrapper_self_hosted_packet_exists_and_declares_roots() -> None:
    text = _read("docs/projects/wrapper_self_hosted.md")
    assert "# Project packet - Wrapper Self Hosted" in text
    assert r"`C:\dev\patchops`" in text
    assert "generic_python" in text
    assert "handoff/current_handoff.md" in text
    assert "export-handoff" in text
    assert "patch_78" in text
    assert "patch_79" in text
