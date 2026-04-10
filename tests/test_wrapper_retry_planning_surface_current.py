from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.workflows.wrapper_retry import (
    WrapperOnlyRetryState,
    build_wrapper_only_retry_state,
    normalize_wrapper_only_retry_reason,
    render_wrapper_only_retry_scope_lines,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_manifest(tmp_path: Path) -> Path:
    manifest_path = tmp_path / "wrapper_retry_manifest.json"
    payload = {
        "manifest_version": "1",
        "patch_name": "wrapper_retry_preview_demo",
        "active_profile": "generic_python",
        "target_project_root": str(tmp_path),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/generated.md",
                "content": "hello\n",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "pytest",
                "program": "py",
                "args": ["-m", "pytest", "-q"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [
            {
                "name": "smoke",
                "program": "py",
                "args": ["--version"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {},
        "tags": ["wrapper_retry", "planning"],
        "notes": "Temporary manifest used by the wrapper-only retry planning-surface test.",
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def test_normalize_wrapper_only_retry_reason_keeps_default_contract() -> None:
    assert normalize_wrapper_only_retry_reason(None)
    assert normalize_wrapper_only_retry_reason("") == normalize_wrapper_only_retry_reason(None)
    assert normalize_wrapper_only_retry_reason("  report   writer   failed  ") == "report writer failed"


def test_build_wrapper_only_retry_state_keeps_retry_narrow_and_write_free(tmp_path: Path) -> None:
    present = tmp_path / "docs" / "present.md"
    present.parent.mkdir(parents=True, exist_ok=True)
    present.write_text("ok\n", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md", "docs/missing.md"],
        "files_to_write": [{"path": "docs/generated.md", "content": "hello"}],
        "validation_commands": [{"name": "pytest", "program": "py", "args": ["-m", "pytest", "-q"]}],
        "smoke_commands": [{"name": "smoke", "program": "py", "args": ["--version"]}],
        "audit_commands": [],
    }

    state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason=" report writer failed after likely validation success ",
    )

    assert isinstance(state, WrapperOnlyRetryState)
    assert state.retry_kind == "wrapper_only_retry"
    assert state.writes_skipped is True
    assert state.explicit_retry_required is True
    assert "generated.md" in "\n".join(state.expected_target_files)
    assert str(present) in state.existing_target_files
    assert any(item.endswith("missing.md") for item in state.missing_target_files)
    scope_lines = render_wrapper_only_retry_scope_lines(state)
    joined = "\n".join(scope_lines).lower()
    assert "wrapper-only retry" in joined or "wrapper only retry" in joined
    assert "writes skipped" in joined or "writes_skipped" in joined
    assert "retry reason" in joined or "reason" in joined


def test_cli_plan_supports_wrapper_retry_mode_preview(tmp_path: Path, capsys) -> None:
    manifest_path = _write_manifest(tmp_path)

    exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--wrapper-root",
            str(PROJECT_ROOT),
            "--mode",
            "wrapper_retry",
            "--retry-reason",
            "report writer failed after likely validation success",
        ]
    )
    captured = capsys.readouterr().out.lower()

    assert exit_code == 0
    assert "wrapper_only_retry" in captured or "wrapper_retry" in captured
    assert "report writer failed after likely validation success" in captured
    assert "writes_skipped" in captured or "writes skipped" in captured


def test_cli_plan_wrapper_retry_preview_reports_missing_targets_when_needed(tmp_path: Path, capsys) -> None:
    manifest_path = _write_manifest(tmp_path)
    exit_code = main(
        [
            "plan",
            str(manifest_path),
            "--wrapper-root",
            str(PROJECT_ROOT),
            "--mode",
            "wrapper_retry",
        ]
    )
    captured = capsys.readouterr().out.lower()

    assert exit_code == 0
    assert "missing" in captured
    assert "generated.md" in captured
