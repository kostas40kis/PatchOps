from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.copied_script_static_validator import (
    BLOCKED_INVALID_SCRIPT,
    PASS_SCRIPT_VALIDATED_RUN_BLOCKED,
    find_latest_staged_script,
    run_copied_script_static_validator,
    validate_copied_script_static_file,
    validate_copied_script_static_text,
)
from patchops.copilot_downloader.script_payload_contract import sha256_text


def _safe_script(extra: str = "") -> str:
    return (
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        "    .\\.venv\\Scripts\\python.exe -m patchops.cli check data/runtime/direct_patches/example/manifest.json\n"
        f"{extra}\n"
        "}\n"
    )


def test_static_validator_accepts_patchops_only_script_and_hashes_without_raw_text():
    script = _safe_script()
    result = validate_copied_script_static_text(script)
    payload = result.to_dict()
    assert result.result_label == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result.ok is True
    assert payload["script_sha256"] == sha256_text(script)
    assert payload["patchops_cli_commands"] == ["check"]
    assert payload["raw_script_logged"] is False
    assert payload["script_executed"] is False
    assert payload["patchops_invoked"] is False
    serialized = json.dumps(payload)
    assert "Set-StrictMode" not in serialized
    assert "patchops.cli check" not in serialized


def test_static_validator_requires_strict_mode_and_invocation_wrapper():
    missing_strict = _safe_script().replace("Set-StrictMode -Version Latest", "Write-Host no strict")
    assert validate_copied_script_static_text(missing_strict).result_label == BLOCKED_INVALID_SCRIPT
    no_wrapper = "Set-StrictMode -Version Latest\n.\\.venv\\Scripts\\python.exe -m patchops.cli check x\n"
    assert validate_copied_script_static_text(no_wrapper).result_label == BLOCKED_INVALID_SCRIPT


def test_static_validator_requires_patchops_cli_and_allows_only_expected_subcommands():
    no_patchops = "& {\n    Set-StrictMode -Version Latest\n}\n"
    assert validate_copied_script_static_text(no_patchops).result_label == BLOCKED_INVALID_SCRIPT
    bad_subcommand = _safe_script("    .\\.venv\\Scripts\\python.exe -m patchops.cli run-package data/runtime/x.zip")
    result = validate_copied_script_static_text(bad_subcommand)
    assert result.result_label == BLOCKED_INVALID_SCRIPT
    assert any("not allowed" in issue for issue in result.issues)


def test_static_validator_blocks_hidden_downloads_and_network_fetches():
    for bad in [
        "    Invoke-WebRequest https://example.invalid/a.ps1",
        "    iwr https://example.invalid/a.ps1",
        "    curl https://example.invalid/a.ps1",
        "    (New-Object System.Net.WebClient).DownloadString('https://example.invalid')",
    ]:
        result = validate_copied_script_static_text(_safe_script(bad))
        assert result.result_label == BLOCKED_INVALID_SCRIPT
        assert "hidden_download_or_network_fetch" in result.blocked_categories


def test_static_validator_blocks_encoded_dynamic_commands():
    for bad in [
        "    powershell.exe -EncodedCommand SQBFAFgA",
        "    [Convert]::FromBase64String('SQBFAFgA')",
        "    Invoke-Expression $payload",
        "    Add-Type -TypeDefinition 'public class X {}'",
    ]:
        result = validate_copied_script_static_text(_safe_script(bad))
        assert result.result_label == BLOCKED_INVALID_SCRIPT
        assert "encoded_or_dynamic_command" in result.blocked_categories


def test_static_validator_blocks_broad_deletes_and_system_mutation():
    for bad in [
        "    Remove-Item C:\\ -Recurse -Force",
        "    rmdir C:\\temp /s",
        "    Set-ExecutionPolicy Unrestricted -Force",
        "    Format-Volume -DriveLetter D",
    ]:
        result = validate_copied_script_static_text(_safe_script(bad))
        assert result.result_label == BLOCKED_INVALID_SCRIPT
        assert any(category in result.blocked_categories for category in ["broad_delete_or_system_mutation", "broad_recursive_delete"])


def test_static_validator_blocks_browser_clipboard_and_uploader_activity():
    for bad, category in [
        ("    Start-Process msedge.exe", "browser_or_clipboard_activity"),
        ("    Get-Clipboard", "browser_or_clipboard_activity"),
        ("    import patchops.chatgpt_uploader", "uploader_activity"),
        ("    Write-Host latest_report_handoff", "uploader_activity"),
    ]:
        result = validate_copied_script_static_text(_safe_script(bad))
        assert result.result_label == BLOCKED_INVALID_SCRIPT
        assert category in result.blocked_categories


def test_static_validator_file_path_and_latest_staged_script_detection(tmp_path: Path):
    repo_root = tmp_path / "repo"
    staged_dir = repo_root / "data" / "runtime" / "copilot_downloader" / "copied_scripts" / "staged" / "abc"
    staged_dir.mkdir(parents=True)
    script_path = staged_dir / "extracted_script.ps1"
    script_path.write_text(_safe_script(), encoding="utf-8")
    assert find_latest_staged_script(repo_root) == script_path
    result = validate_copied_script_static_file(script_path)
    assert result.result_label == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result.script_path == str(script_path)


def test_static_validator_doctor_uses_sample_when_no_staged_script_and_does_not_run(tmp_path: Path):
    result = run_copied_script_static_validator(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["used_embedded_sample"] is True
    assert result["checks"]["script_not_executed"] is True
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True
    assert result["checks"]["run_not_authorized"] is True
    assert result["safety"]["artifact_executed"] is False
    assert result["safety"]["patchops_invoked"] is False
    evidence_json = Path(result["evidence_files"]["json"])
    assert evidence_json.is_file()
    serialized = evidence_json.read_text(encoding="utf-8")
    assert "patchops.cli check" not in serialized
    assert "Set-StrictMode" not in serialized


def test_static_validator_doctor_validates_explicit_staged_script_path(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path = repo_root / "extracted_script.ps1"
    script_path.write_text(_safe_script("    .\\.venv\\Scripts\\python.exe -m patchops.cli verify data/runtime/direct_patches/example/manifest.json"), encoding="utf-8")
    result = run_copied_script_static_validator(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_script_path=script_path)
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["used_embedded_sample"] is False
    assert result["validation_result"]["patchops_cli_commands"] == ["check", "verify"]
    assert result["checks"]["run_not_authorized"] is True


def test_repository_static_validator_doctor_is_green_without_clipboard_browser_or_run():
    result = run_copied_script_static_validator(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d2_03_static_validator_test",
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["browser_not_used"] is True
    assert result["checks"]["uploader_not_imported"] is True
    assert result["checks"]["run_not_authorized"] is True