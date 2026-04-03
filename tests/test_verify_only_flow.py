from pathlib import Path

from patchops.workflows.verify_only import (
    VerifyOnlyFlowState,
    build_verify_only_flow_state,
    render_verify_only_scope_lines,
    resolve_verify_only_expected_target_files,
    verify_only_flow_needs_attention,
)
from patchops.workflows.wrapper_retry import (
    WrapperOnlyRetryState,
    build_wrapper_only_retry_state,
    render_wrapper_only_retry_scope_lines,
    wrapper_only_retry_allows_writes,
    wrapper_only_retry_needs_escalation,
)


def test_resolve_verify_only_expected_target_files_preserves_order_and_deduplicates(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/one.md", "docs/one.md", "docs/two.md"],
        "files_to_write": [
            {"path": "docs/two.md", "content": "hello"},
            {"path": "docs/three.md", "content": "world"},
            {"path": str(tmp_path / "absolute.txt"), "content": "ok"},
        ],
    }

    resolved = resolve_verify_only_expected_target_files(manifest, tmp_path)

    assert resolved == [
        str(tmp_path / "docs" / "one.md"),
        str(tmp_path / "docs" / "two.md"),
        str(tmp_path / "docs" / "three.md"),
        str(tmp_path / "absolute.txt"),
    ]


def test_build_verify_only_flow_state_tracks_clear_daily_use_counts(tmp_path: Path) -> None:
    present = tmp_path / "docs" / "present.md"
    present.parent.mkdir(parents=True, exist_ok=True)
    present.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md", "docs/missing.md"],
        "validation_commands": [
            {"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]},
            {"name": "lint", "program": "python", "args": ["-m", "ruff", "check", "."]},
        ],
        "smoke_commands": [{"name": "smoke", "program": "python", "args": ["--version"]}],
        "audit_commands": [{"name": "audit", "program": "python", "args": ["--version"]}],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)

    assert isinstance(state, VerifyOnlyFlowState)
    assert state.mode == "verify"
    assert state.writes_skipped is True
    assert state.expected_target_files == (
        str(tmp_path / "docs" / "present.md"),
        str(tmp_path / "docs" / "missing.md"),
    )
    assert state.existing_target_files == (str(present),)
    assert state.missing_target_files == (str(tmp_path / "docs" / "missing.md"),)
    assert state.validation_command_count == 2
    assert state.smoke_command_count == 1
    assert state.audit_command_count == 1


def test_render_verify_only_scope_lines_make_rerun_boundary_obvious(tmp_path: Path) -> None:
    present = tmp_path / "docs" / "present.md"
    present.parent.mkdir(parents=True, exist_ok=True)
    present.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md", "docs/missing.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
        "smoke_commands": [{"name": "smoke", "program": "python", "args": ["--version"]}],
        "audit_commands": [],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)
    lines = render_verify_only_scope_lines(state)

    assert "Scope    : verification-only rerun" in lines
    assert "Mode     : verify" in lines
    assert "Writes   : skipped" in lines
    assert "Intent   : re-check files already on disk and rerun validation commands" in lines
    assert "Expected : 2" in lines
    assert "Existing : 1" in lines
    assert "Missing  : 1" in lines
    assert "Validate : 1" in lines
    assert "Smoke    : 1" in lines
    assert "Audit    : 0" in lines


def test_verify_only_flow_with_no_expected_files_stays_narrow_and_non_escalating(tmp_path: Path) -> None:
    manifest = {
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
        "smoke_commands": [],
        "audit_commands": [],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)
    lines = render_verify_only_scope_lines(state)

    assert state.expected_target_files == ()
    assert state.existing_target_files == ()
    assert state.missing_target_files == ()
    assert verify_only_flow_needs_attention(state) is False
    assert "Expected : 0" in lines
    assert "Existing : 0" in lines
    assert "Missing  : 0" in lines


def test_verify_only_and_wrapper_retry_both_skip_writes_but_keep_distinct_scope(tmp_path: Path) -> None:
    present = tmp_path / "docs" / "present.md"
    present.parent.mkdir(parents=True, exist_ok=True)
    present.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
    }

    verify_state = build_verify_only_flow_state(manifest, tmp_path)
    retry_state = build_wrapper_only_retry_state(
        manifest,
        tmp_path,
        reason="report writer failed after validation",
    )

    verify_lines = render_verify_only_scope_lines(verify_state)
    retry_lines = render_wrapper_only_retry_scope_lines(retry_state)

    assert isinstance(retry_state, WrapperOnlyRetryState)
    assert verify_state.writes_skipped is True
    assert retry_state.writes_skipped is True
    assert verify_only_flow_needs_attention(verify_state) is False
    assert wrapper_only_retry_needs_escalation(retry_state) is False
    assert wrapper_only_retry_allows_writes(retry_state) is False
    assert "Scope    : verification-only rerun" in verify_lines
    assert "Scope    : wrapper-only retry" in retry_lines
    assert "Writes   : skipped" in verify_lines
    assert "Writes   : skipped" in retry_lines
    assert "Escalate : stay narrow" in retry_lines


def test_missing_expected_files_make_both_paths_honest_about_attention(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/missing.md"],
        "validation_commands": [],
    }

    verify_state = build_verify_only_flow_state(manifest, tmp_path)
    retry_state = build_wrapper_only_retry_state(manifest, tmp_path)
    retry_lines = render_wrapper_only_retry_scope_lines(retry_state)

    assert verify_only_flow_needs_attention(verify_state) is True
    assert wrapper_only_retry_needs_escalation(retry_state) is True
    assert wrapper_only_retry_allows_writes(retry_state) is False
    assert "Missing  : 1" in retry_lines
    assert "Escalate : full apply review required" in retry_lines
