from pathlib import Path


def test_operator_guidance_quickstart_mentions_current_operator_surfaces() -> None:
    quickstart = Path("docs/operator_quickstart.md").read_text(encoding="utf-8")
    assert "patchops.bootstrap_repair" in quickstart
    assert "bootstrap-repair" in quickstart
    assert "emit-operator-script" in quickstart
    assert "maintenance-gate" in quickstart
    assert "Push-PatchOpsToGitHub.ps1" in quickstart
    assert "docs/root_launcher_shape_contract.md" in quickstart
    assert "docs/post_publish_snapshot.md" in quickstart
    assert "Return to the normal `check` / `inspect` / `plan` / `apply` / `verify`" in quickstart


def test_failure_repair_guide_mentions_wrapper_boundary_and_launcher_artifacts() -> None:
    text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8")
    assert "wrapper failure versus target-content failure" in text
    assert "not a second apply engine" in text
    assert "stray leading characters in `run_with_patchops.ps1`" in text
    assert "emit-operator-script" in text
    assert "maintenance-gate" in text
    assert "Push-PatchOpsToGitHub.ps1" in text


def test_doc_reading_order_points_to_current_first_read_surfaces() -> None:
    text = Path("docs/doc_reading_order.md").read_text(encoding="utf-8")
    assert "docs/operator_quickstart.md" in text
    assert "docs/failure_repair_guide.md" in text
    assert "docs/post_publish_snapshot.md" in text
    assert "docs/root_launcher_shape_contract.md" in text
    assert "docs/github_publish_helper.md" in text
