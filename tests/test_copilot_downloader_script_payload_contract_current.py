from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.script_payload_contract import (
    BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
    PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED,
    REQUIRED_CONFIRMATION,
    REQUIRED_TYPE,
    SCRIPT_BEGIN,
    SCRIPT_END,
    build_example_payload,
    run_script_payload_contract_doctor,
    sha256_text,
    validate_script_payload_contract_file,
    validate_script_payload_contract_text,
)


def test_valid_contract_payload_has_required_metadata_hashes_and_no_raw_script():
    text = build_example_payload("d2_01_example")
    result = validate_script_payload_contract_text(text)
    payload = result.to_dict()
    assert result.result_label == PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED
    assert result.ok is True
    assert payload["metadata"] == {
        "name": "d2_01_example",
        "type": REQUIRED_TYPE,
        "requires_confirmation": REQUIRED_CONFIRMATION,
    }
    assert len(payload["payload_sha256"]) == 64
    assert len(payload["script_sha256"]) == 64
    serialized = json.dumps(payload)
    assert "Write-Host" not in serialized
    assert "Set-StrictMode" not in serialized
    assert payload["raw_payload_logged"] is False
    assert payload["raw_script_logged"] is False


def test_no_marker_blocks_no_extraction():
    result = validate_script_payload_contract_text("& { Set-StrictMode -Version Latest }")
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("markers" in issue for issue in result.issues)


def test_multiple_marker_pairs_are_blocked():
    result = validate_script_payload_contract_text(build_example_payload("one") + "\n" + build_example_payload("two"))
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("multiple" in issue or "exactly one" in issue for issue in result.issues)


def test_missing_invocation_block_is_blocked():
    text = f"{SCRIPT_BEGIN}\nname: d_bad\ntype: {REQUIRED_TYPE}\nrequires_confirmation: {REQUIRED_CONFIRMATION}\n{SCRIPT_END}\n"
    result = validate_script_payload_contract_text(text)
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("& {" in issue for issue in result.issues)


def test_missing_strict_mode_is_blocked():
    text = build_example_payload("d_bad_strict").replace("Set-StrictMode -Version Latest", "Write-Host missing strict")
    result = validate_script_payload_contract_text(text)
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("Set-StrictMode" in issue for issue in result.issues)


def test_missing_required_metadata_is_blocked():
    text = (
        f"{SCRIPT_BEGIN}\n"
        f"type: {REQUIRED_TYPE}\n"
        f"requires_confirmation: {REQUIRED_CONFIRMATION}\n\n"
        "& {\n    Set-StrictMode -Version Latest\n}\n"
        f"{SCRIPT_END}\n"
    )
    result = validate_script_payload_contract_text(text)
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("name" in issue for issue in result.issues)


def test_wrong_type_or_confirmation_is_blocked():
    wrong_type = build_example_payload("d_wrong_type").replace(REQUIRED_TYPE, "plain_text")
    wrong_confirmation = build_example_payload("d_wrong_confirm").replace(REQUIRED_CONFIRMATION, "WRONG_CONFIRM")
    assert validate_script_payload_contract_text(wrong_type).result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert validate_script_payload_contract_text(wrong_confirmation).result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID


def test_invalid_patch_name_is_blocked():
    text = build_example_payload("bad name with spaces")
    result = validate_script_payload_contract_text(text)
    assert result.result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID
    assert any("name" in issue for issue in result.issues)


def test_contract_file_validator_uses_utf8_file(tmp_path: Path):
    path = tmp_path / "payload.ps1"
    text = build_example_payload("d_file_contract")
    path.write_text(text, encoding="utf-8")
    result = validate_script_payload_contract_file(path)
    assert result.result_label == PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED
    assert result.payload_sha256 == sha256_text(text[text.index(SCRIPT_BEGIN):text.index(SCRIPT_END) + len(SCRIPT_END)])


def test_contract_doctor_writes_redacted_evidence_and_no_clipboard_or_execution(tmp_path: Path):
    result = run_script_payload_contract_doctor(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["browser_not_used"] is True
    assert result["checks"]["artifact_not_executed"] is True
    assert result["checks"]["raw_payload_not_logged"] is True
    assert result["safety"]["clipboard_read"] is False
    assert result["safety"]["artifact_executed"] is False
    evidence_json = Path(result["evidence_files"]["json"])
    evidence_text = Path(result["evidence_files"]["text"])
    assert evidence_json.is_file()
    assert evidence_text.is_file()
    serialized = evidence_json.read_text(encoding="utf-8")
    assert "PatchOps marker contract sample only" not in serialized
    assert "Set-StrictMode" not in serialized


def test_repository_contract_doctor_is_green_without_browser_or_clipboard():
    result = run_script_payload_contract_doctor(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d2_01_script_payload_contract_test",
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True
    assert result["checks"]["uploader_not_imported"] is True