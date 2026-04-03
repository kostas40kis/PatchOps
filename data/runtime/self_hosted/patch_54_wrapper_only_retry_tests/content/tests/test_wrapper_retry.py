import json
from pathlib import Path

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.workflows import wrapper_retry as wrapper_retry_module
from patchops.workflows.wrapper_retry import (
    DEFAULT_WRAPPER_ONLY_RETRY_REASON,
    WrapperOnlyRetryState,
    build_wrapper_only_retry_state,
    execute_wrapper_only_retry,
    normalize_wrapper_only_retry_reason,
    render_wrapper_only_retry_scope_lines,
    wrapper_only_retry_allows_writes,
    wrapper_only_retry_needs_escalation,
    wrapper_only_retry_state_as_dict,
)


def test_normalize_wrapper_only_retry_reason_defaults_cleanly() -> None:
    assert normalize_wrapper_only_retry_reason(None) == DEFAULT_WRAPPER_ONLY_RETRY_REASON
    assert normalize_wrapper_only_retry_reason("") == DEFAULT_WRAPPER_ONLY_RETRY_REASON
    assert normalize_wrapper_only_retry_reason("  wrapper   report   failed  ") == "wrapper report failed"


def test_build_wrapper_only_retry_state_reuses_expected_target_resolution(tmp_path: Path) -> None:
    existing_file = tmp_path / "docs" / "present.md"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md", "docs/missing.md"],
        "files_to_write": [{"path": "docs/generated.md", "content": "hello"}],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
        "smoke_commands": [{"name": "smoke", "program": "python", "args": ["--version"]}],
        "audit_commands": [{"name": "audit", "program": "python", "args": ["--version"]}],
    }

    state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason=" report writer failed after tests passed ",
    )

    assert isinstance(state, WrapperOnlyRetryState)
    assert state.mode == "verify"
    assert state.retry_kind == "wrapper_only_retry"
    assert state.writes_skipped is True
    assert state.explicit_retry_required is True
    assert state.reason == "report writer failed after tests passed"
    assert state.expected_target_files == (
        str(tmp_path / "docs" / "present.md"),
        str(tmp_path / "docs" / "missing.md"),
        str(tmp_path / "docs" / "generated.md"),
    )
    assert state.existing_target_files == (str(existing_file),)
    assert state.missing_target_files == (
        str(tmp_path / "docs" / "missing.md"),
        str(tmp_path / "docs" / "generated.md"),
    )
    assert state.validation_command_count == 1
    assert state.smoke_command_count == 1
    assert state.audit_command_count == 1


def test_render_wrapper_only_retry_scope_lines_make_narrow_retry_explicit(tmp_path: Path) -> None:
    present_file = tmp_path / "docs" / "present.md"
    present_file.parent.mkdir(parents=True, exist_ok=True)
    present_file.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
    }

    state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason="report writer failed after validation",
    )
    lines = render_wrapper_only_retry_scope_lines(state)

    assert "Scope    : wrapper-only retry" in lines
    assert "Mode     : verify" in lines
    assert "Kind     : wrapper_only_retry" in lines
    assert "Writes   : skipped" in lines
    assert "Intent   : recover evidence/reporting after likely wrapper failure" in lines
    assert "Reason   : report writer failed after validation" in lines
    assert "Explicit : yes" in lines
    assert "Expected : 1" in lines
    assert "Existing : 1" in lines
    assert "Missing  : 0" in lines
    assert "Validate : 1" in lines
    assert "Smoke    : 0" in lines
    assert "Audit    : 0" in lines
    assert "Escalate : stay narrow" in lines


def test_missing_expected_files_force_escalation_and_still_disallow_writes(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/missing.md"],
        "validation_commands": [],
    }

    state = build_wrapper_only_retry_state(manifest, tmp_path)

    assert wrapper_only_retry_needs_escalation(state) is True
    assert wrapper_only_retry_allows_writes(state) is False


def test_wrapper_only_retry_state_as_dict_is_planning_friendly(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/missing.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
    }

    state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason=" report writer failed after likely success ",
    )
    payload = wrapper_only_retry_state_as_dict(state)

    assert payload["mode"] == "verify"
    assert payload["retry_kind"] == "wrapper_only_retry"
    assert payload["reason"] == "report writer failed after likely success"
    assert payload["writes_skipped"] is True
    assert payload["explicit_retry_required"] is True
    assert payload["expected_target_files"] == [str(tmp_path / "docs" / "missing.md")]
    assert payload["existing_target_files"] == []
    assert payload["missing_target_files"] == [str(tmp_path / "docs" / "missing.md")]
    assert payload["validation_command_count"] == 1
    assert payload["smoke_command_count"] == 0
    assert payload["audit_command_count"] == 0
    assert payload["needs_escalation"] is True
    assert payload["allows_writes"] is False
    assert "Scope    : wrapper-only retry" in payload["scope_lines"]
    assert "Escalate : full apply review required" in payload["scope_lines"]


def test_wrapper_only_retry_state_as_dict_stays_narrow_when_expected_files_exist(tmp_path: Path) -> None:
    present_file = tmp_path / "docs" / "present.md"
    present_file.parent.mkdir(parents=True, exist_ok=True)
    present_file.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md"],
        "validation_commands": [],
    }

    state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason="report writer failed after likely success",
    )
    payload = wrapper_only_retry_state_as_dict(state)

    assert payload["writes_skipped"] is True
    assert payload["expected_target_files"] == [str(present_file)]
    assert payload["existing_target_files"] == [str(present_file)]
    assert payload["missing_target_files"] == []
    assert payload["needs_escalation"] is False
    assert payload["allows_writes"] is False
    assert "Escalate : stay narrow" in payload["scope_lines"]


def test_execute_wrapper_only_retry_delegates_to_verify_only_and_relabels_mode(tmp_path: Path, monkeypatch) -> None:
    manifest = Manifest(
        manifest_version="1",
        patch_name="wrapper_retry_exec",
        active_profile="generic_python",
        files_to_write=[],
    )
    manifest_path = tmp_path / "wrapper_retry_exec.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "wrapper_retry_exec",
                "active_profile": "generic_python",
                "target_project_root": str(tmp_path).replace("\\", "/"),
                "files_to_write": [],
            }
        ),
        encoding="utf-8",
    )

    fake_result = WorkflowResult(
        mode="verify_only",
        manifest_path=manifest_path,
        manifest=manifest,
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path,
        runtime_path=None,
        backup_root=None,
        report_path=tmp_path / "wrapper_retry_exec_report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=0,
        result_label="PASS",
    )

    monkeypatch.setattr(
        wrapper_retry_module,
        "verify_only",
        lambda manifest_path, wrapper_project_root=None: fake_result,
    )

    result = execute_wrapper_only_retry(
        manifest_path,
        wrapper_project_root=tmp_path,
        reason=" report writer failed after validation ",
    )

    assert result.mode == "wrapper_only_retry"
    assert result.report_path == fake_result.report_path


def test_execute_wrapper_only_retry_passes_resolved_wrapper_root_to_verify_only(tmp_path: Path, monkeypatch) -> None:
    manifest_path = tmp_path / "wrapper_retry_exec_root.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "wrapper_retry_exec_root",
                "active_profile": "generic_python",
                "target_project_root": str(tmp_path).replace("\\", "/"),
                "files_to_write": [],
            }
        ),
        encoding="utf-8",
    )

    captured = {}

    fake_result = WorkflowResult(
        mode="verify_only",
        manifest_path=manifest_path,
        manifest=Manifest(
            manifest_version="1",
            patch_name="wrapper_retry_exec_root",
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
        target_project_root=tmp_path,
        runtime_path=None,
        backup_root=None,
        report_path=tmp_path / "wrapper_retry_exec_root_report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=0,
        result_label="PASS",
    )

    def _fake_verify_only(manifest_path, wrapper_project_root=None):
        captured["manifest_path"] = manifest_path
        captured["wrapper_project_root"] = wrapper_project_root
        return fake_result

    monkeypatch.setattr(wrapper_retry_module, "verify_only", _fake_verify_only)

    result = execute_wrapper_only_retry(
        manifest_path,
        wrapper_project_root=tmp_path,
        reason="report writer failed after validation",
    )

    assert result.mode == "wrapper_only_retry"
    assert Path(captured["manifest_path"]) == manifest_path.resolve()
    assert Path(captured["wrapper_project_root"]) == tmp_path.resolve()


def test_wrapper_only_retry_defaults_do_not_claim_write_capability(tmp_path: Path) -> None:
    manifest = {"validation_commands": []}
    state = build_wrapper_only_retry_state(manifest, tmp_path)

    assert state.reason == DEFAULT_WRAPPER_ONLY_RETRY_REASON
    assert wrapper_only_retry_allows_writes(state) is False