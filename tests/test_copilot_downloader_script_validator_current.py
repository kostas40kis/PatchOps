from __future__ import annotations

from pathlib import Path

from patchops.copilot_downloader.script_validator import validate_patchops_script_payload_text


def _good_payload(body: str = "") -> str:
    return (
        "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\n"
        "name: d_example\n"
        "type: patchops_powershell_script\n"
        "requires_confirmation: PATCHOPS_CONFIRM_RUN\n\n"
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        f"{body}\n"
        "}\n"
        "PATCHOPS_SCRIPT_PAYLOAD_END\n"
    )


def test_valid_marked_script_payload_passes_and_remains_run_blocked():
    result = validate_patchops_script_payload_text(_good_payload("    .\\.venv\\Scripts\\python.exe -m patchops.cli check data/runtime/direct_patches/x/manifest.json"))
    assert result.result_label == "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"
    assert result.ok is True
    assert result.checks["single_payload_marker_pair"] is True
    assert result.checks["script_surrounded_by_invocation_block"] is True
    assert result.checks["strict_mode_present"] is True


def test_multiple_payload_markers_are_blocked():
    text = _good_payload() + _good_payload()
    result = validate_patchops_script_payload_text(text)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert any("expected exactly one PATCHOPS_SCRIPT_PAYLOAD_BEGIN" in issue for issue in result.issues)


def test_missing_invocation_block_is_blocked():
    text = "PATCHOPS_SCRIPT_PAYLOAD_BEGIN\nSet-StrictMode -Version Latest\nPATCHOPS_SCRIPT_PAYLOAD_END\n"
    result = validate_patchops_script_payload_text(text)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "script must be surrounded by & { ... }" in result.issues


def test_missing_strict_mode_is_blocked():
    text = _good_payload().replace("Set-StrictMode -Version Latest", "Write-Host hi")
    result = validate_patchops_script_payload_text(text)
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "Set-StrictMode is required" in result.issues


def test_encoded_command_and_hidden_download_are_blocked():
    result = validate_patchops_script_payload_text(_good_payload("    powershell.exe -EncodedCommand SQBFAFg=\n    Invoke-WebRequest https://example.invalid/a.ps1"))
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "blocked_pattern:encoded_command" in result.issues
    assert "blocked_pattern:hidden_download" in result.issues


def test_destructive_commands_are_blocked():
    result = validate_patchops_script_payload_text(_good_payload("    Remove-Item C:\\temp\\x -Recurse -Force"))
    assert result.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "blocked_pattern:destructive_remove" in result.issues


def test_git_commit_or_push_requires_explicit_authorization():
    blocked = validate_patchops_script_payload_text(_good_payload("    git commit -m test\n    git push"))
    assert blocked.result_label == "BLOCKED_INVALID_ARTIFACT"
    assert "git_commit_without_explicit_authorization" in blocked.issues
    assert "git_push_without_explicit_authorization" in blocked.issues

    allowed = validate_patchops_script_payload_text(_good_payload("    # PATCHOPS_ALLOW_GIT_WRITE\n    git commit -m test"))
    assert "git_commit_without_explicit_authorization" not in allowed.issues