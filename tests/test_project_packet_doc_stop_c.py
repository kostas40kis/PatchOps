from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_workflow_doc_has_self_hosted_command_flow() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text


def test_operator_quickstart_mentions_project_packet_commands() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "one canonical report" in text


def test_project_status_tracks_shipped_and_remaining_packet_work() -> None:
    text = _read("docs/project_status.md")
    assert "PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:START" in text
    assert "wrapper_self_hosted.md" in text
    assert "profile recommendation helper" in text
    assert "starter helper by intent" in text
