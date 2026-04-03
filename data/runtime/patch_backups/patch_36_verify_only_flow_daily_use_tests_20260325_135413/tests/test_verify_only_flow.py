from pathlib import Path

from patchops.workflows.verify_only import (
    VerifyOnlyFlowState,
    build_verify_only_flow_state,
    render_verify_only_scope_lines,
    resolve_verify_only_expected_target_files,
    verify_only_flow_needs_attention,
)



def test_resolve_verify_only_expected_target_files_uses_target_files_and_files_to_write(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/one.md", "docs/one.md"],
        "files_to_write": [
            {"path": "docs/two.md", "content": "hello"},
            {"path": str(tmp_path / "absolute.txt"), "content": "world"},
        ],
    }

    resolved = resolve_verify_only_expected_target_files(manifest, tmp_path)

    assert resolved == [
        str(tmp_path / "docs" / "one.md"),
        str(tmp_path / "docs" / "two.md"),
        str(tmp_path / "absolute.txt"),
    ]



def test_build_verify_only_flow_state_tracks_existing_and_missing_files(tmp_path: Path) -> None:
    existing_file = tmp_path / "docs" / "present.md"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md", "docs/missing.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
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
    assert state.existing_target_files == (str(existing_file),)
    assert state.missing_target_files == (str(tmp_path / "docs" / "missing.md"),)
    assert state.validation_command_count == 1
    assert state.smoke_command_count == 1
    assert state.audit_command_count == 1



def test_render_verify_only_scope_lines_makes_rerun_scope_explicit(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/only.md"],
        "validation_commands": [{"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]}],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)
    lines = render_verify_only_scope_lines(state)

    assert "Scope    : verification-only rerun" in lines
    assert "Writes   : skipped" in lines
    assert "Intent   : re-check files already on disk and rerun validation commands" in lines
    assert any(line.startswith("Expected : 1") for line in lines)
    assert any(line.startswith("Validate : 1") for line in lines)



def test_verify_only_flow_needs_attention_when_expected_files_are_missing(tmp_path: Path) -> None:
    manifest = {
        "target_files": ["docs/missing.md"],
        "validation_commands": [],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)

    assert verify_only_flow_needs_attention(state) is True



def test_verify_only_flow_does_not_need_attention_when_all_expected_files_exist(tmp_path: Path) -> None:
    existing_file = tmp_path / "docs" / "present.md"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_text("ok", encoding="utf-8")

    manifest = {
        "target_files": ["docs/present.md"],
        "validation_commands": [],
    }

    state = build_verify_only_flow_state(manifest, tmp_path)

    assert verify_only_flow_needs_attention(state) is False
