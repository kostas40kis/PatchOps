from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_project_packet_contract_mentions_packet_home_and_required_sections() -> None:
    text = _read("docs/project_packet_contract.md")
    assert "docs/projects/" in text
    assert "docs/projects/trader.md" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "what must remain outside PatchOps" in text
    assert "next recommended action" in text
    assert "replacement for manifests" in text


def test_project_packet_workflow_mentions_packet_commands_and_handoff_relationship() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "py -m patchops.cli init-project-doc" in text
    assert "py -m patchops.cli refresh-project-doc" in text
    assert "py -m patchops.cli export-handoff" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "A project packet gives target context." in text
    assert "A canonical report gives the evidence." in text


def test_wrapper_self_hosted_packet_matches_post_publish_state() -> None:
    text = _read("docs/projects/wrapper_self_hosted.md")
    assert r"C:\dev\patchops" in text
    assert "generic_python" in text
    assert "docs/post_publish_snapshot.md" in text
    assert "PatchOps remains in maintenance mode." in text
    assert "patch_29a_operator_quickstart_run_package_zip_contract_restore" in text
    assert "continue with narrow maintenance patches" in text
