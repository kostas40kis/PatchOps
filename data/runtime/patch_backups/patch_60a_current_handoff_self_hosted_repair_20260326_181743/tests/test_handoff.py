from pathlib import Path

import patchops.cli as cli
from patchops.handoff import render_current_handoff_lines, write_current_handoff
from patchops.models import FailureInfo, Manifest, ResolvedProfile, WorkflowResult


def _build_result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    patch_name: str = "patch_60_current_handoff_artifact",
    exit_code: int = 0,
    result_label: str = "PASS",
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


def test_render_current_handoff_lines_include_resume_fields(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    lines = render_current_handoff_lines(result)

    assert "# PatchOps current handoff" in lines
    assert "Current Stage         : Stage 2 in progress" in lines
    assert "Current Status        : pass" in lines
    assert "Latest Attempted Patch: Patch 60" in lines
    assert "Latest Passed Patch   : Patch 60" in lines
    assert "Failure Class         : none" in lines
    assert "Next Recommended Mode : new_patch" in lines
    assert any("docs/llm_usage.md" in line for line in lines)


def test_write_current_handoff_writes_expected_file(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    written = write_current_handoff(result)

    handoff_path = Path(written)
    assert handoff_path == tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Run Mode       : apply" in text
    assert "Latest Report Path    : " in text
    assert "Do Not Redesign       : Keep PowerShell thin and reusable logic in Python unless the evidence forces deeper change." in text


def test_failed_handoff_represents_target_failure_honestly(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        mode="apply",
        result_label="FAIL",
        exit_code=1,
        failure=FailureInfo(category="target_project_failure", message="docs failed"),
    )

    text = "\n".join(render_current_handoff_lines(result))
    assert "Current Status        : fail" in text
    assert "Latest Passed Patch   : unknown from this run" in text
    assert "Failure Class         : target_project_failure" in text
    assert "Next Recommended Mode : repair_patch" in text
    assert "Keep the repair narrow." in text


def test_cli_apply_command_updates_current_handoff(tmp_path: Path, monkeypatch) -> None:
    fake_result = _build_result(tmp_path, mode="apply")
    monkeypatch.setattr(cli, "apply_manifest", lambda manifest, wrapper_project_root=None: fake_result)

    exit_code = cli.main(["apply", "example.json", "--wrapper-root", str(tmp_path)])

    assert exit_code == 0
    handoff_path = tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Attempted Patch: Patch 60" in text
    assert "Next Recommended Mode : new_patch" in text


def test_cli_wrapper_retry_command_updates_current_handoff_with_retry_mode(tmp_path: Path, monkeypatch) -> None:
    fake_result = _build_result(tmp_path, mode="wrapper_only_retry")
    monkeypatch.setattr(
        cli,
        "execute_wrapper_only_retry",
        lambda manifest, wrapper_project_root=None, reason=None: fake_result,
    )

    exit_code = cli.main(
        [
            "wrapper-retry",
            "example.json",
            "--wrapper-root",
            str(tmp_path),
            "--retry-reason",
            "report writer failed after validation",
        ]
    )

    assert exit_code == 0
    handoff_path = tmp_path / "handoff" / "current_handoff.md"
    assert handoff_path.exists()

    text = handoff_path.read_text(encoding="utf-8")
    assert "Latest Run Mode       : wrapper_only_retry" in text