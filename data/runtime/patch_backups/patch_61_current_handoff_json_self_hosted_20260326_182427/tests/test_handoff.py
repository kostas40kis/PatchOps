from pathlib import Path

from patchops.handoff import render_current_handoff_lines, write_current_handoff
from patchops.models import FailureInfo, Manifest, ResolvedProfile, WorkflowResult


def _build_result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    patch_name: str = "patch_60_current_handoff_artifact",
    result_label: str = "PASS",
    exit_code: int = 0,
    failure: FailureInfo | None = None,
) -> WorkflowResult:
    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name=patch_name,
            active_profile="generic_python",
            files_to_write=[],
        ),
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path / "target_project",
        runtime_path=None,
        backup_root=tmp_path / "backup_root",
        report_path=tmp_path / f"{mode}_report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=failure,
        exit_code=exit_code,
        result_label=result_label,
    )


def test_render_current_handoff_lines_for_green_result() -> None:
    result = _build_result(Path("/tmp/patchops_green"))
    lines = render_current_handoff_lines(result)
    text = "\n".join(lines)

    assert "# PatchOps current handoff" in text
    assert "Current Stage         : Stage 2 in progress" in text
    assert "Latest Run Mode       : apply" in text
    assert "Current Status        : pass" in text
    assert "Latest Attempted Patch: Patch 60" in text
    assert "Latest Passed Patch   : Patch 60" in text
    assert "Failure Class         : none" in text
    assert "Next Recommended Mode : new_patch" in text
    assert "Continue with Patch 61." in text
    assert "`docs/llm_usage.md`" in text


def test_render_current_handoff_lines_for_target_failure() -> None:
    result = _build_result(
        Path("/tmp/patchops_fail"),
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="target_project_failure", message="docs failed"),
    )
    text = "\n".join(render_current_handoff_lines(result))

    assert "Current Status        : fail" in text
    assert "Latest Passed Patch   : unknown from this run" in text
    assert "Failure Class         : target_project_failure" in text
    assert "Next Recommended Mode : repair_patch" in text
    assert "Keep the repair narrow. Write a repair patch for the failed target surface." in text


def test_render_current_handoff_lines_for_wrapper_failure() -> None:
    result = _build_result(
        Path("/tmp/patchops_wrapper_fail"),
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="wrapper_failure", message="report write failed"),
    )
    text = "\n".join(render_current_handoff_lines(result))

    assert "Failure Class         : wrapper_failure" in text
    assert "Next Recommended Mode : wrapper_only_retry" in text
    assert "Prefer wrapper-only retry or wrapper-only repair." in text


def test_write_current_handoff_writes_default_file() -> None:
    tmp_path = Path.cwd() / "data" / "runtime" / "test_handoff_write_tmp"
    if tmp_path.exists():
        import shutil
        shutil.rmtree(tmp_path)

    tmp_path.mkdir(parents=True, exist_ok=True)
    result = _build_result(tmp_path)

    written = write_current_handoff(result)
    handoff_path = Path(written)

    assert handoff_path == tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Report Path    : " in text
    assert "Do Not Redesign       : Keep PowerShell thin and reusable logic in Python unless the evidence forces deeper change." in text

    import shutil
    shutil.rmtree(tmp_path)