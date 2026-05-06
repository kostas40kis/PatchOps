from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.browser_target_config import write_default_browser_target_config
from patchops.copilot_downloader.clipboard_probe import CLIPBOARD_CONFIRM_TEXT
from patchops.copilot_downloader.copied_script_extractor import (
    BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE,
    BLOCKED_SCRIPT_EXTRACTION_EMPTY,
    BLOCKED_SCRIPT_EXTRACTION_INVALID,
    BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED,
    BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE,
    PASS_SCRIPT_EXTRACTED_RUN_BLOCKED,
    run_copied_script_extractor,
    stage_extracted_script,
)
from patchops.copilot_downloader.script_payload_contract import SCRIPT_BEGIN, SCRIPT_END, build_example_payload, sha256_text


def _repo_with_browser_config(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    config_path = repo_root / "data" / "config" / "copilot_downloader_browser_target.json"
    write_default_browser_target_config(config_path)
    return repo_root, config_path


def test_non_live_extractor_blocks_controlled_and_does_not_read_clipboard(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"value": False}

    def provider():
        called["value"] = True
        return build_example_payload("should_not_read")

    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=False,
        clipboard_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED
    assert result["issue"] == "live_clipboard_flag_required"
    assert called["value"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["staged_script"] is None
    assert Path(result["evidence_files"]["json"]).is_file()


def test_live_extractor_wrong_confirmation_blocks_and_does_not_read_clipboard(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    called = {"value": False}

    def provider():
        called["value"] = True
        return build_example_payload("should_not_read")

    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text="wrong",
        clipboard_provider=provider,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED
    assert result["issue"] == "clipboard_confirmation_required"
    assert called["value"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["staged_script"] is None


def test_live_extractor_extracts_exactly_one_marked_script_stages_hashes_and_stops_before_run(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    raw_prefix = "RAW_BROWSER_COPY_PREFIX_SENTINEL_d2_02"
    raw_suffix = "RAW_BROWSER_COPY_SUFFIX_SENTINEL_d2_02"
    copied = f"{raw_prefix}\n" + build_example_payload("d2_02_valid") + f"\n{raw_suffix}"

    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: copied,
    )

    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_EXTRACTED_RUN_BLOCKED
    assert result["safety"]["clipboard_read"] is True
    assert result["safety"]["artifact_executed"] is False
    assert result["checks"]["stop_before_static_validation"] is True
    assert result["checks"]["stop_before_run"] is True
    staged = result["staged_script"]
    assert Path(staged["script_path"]).is_file()
    assert Path(staged["metadata_path"]).is_file()
    assert staged["validation_performed"] is False
    assert staged["run_authorized"] is False
    assert staged["script_executed"] is False
    script_text = Path(staged["script_path"]).read_text(encoding="utf-8")
    assert script_text.startswith("& {")
    assert "Set-StrictMode -Version Latest" in script_text
    assert staged["script_sha256"] == sha256_text(script_text)
    serialized = json.dumps(result)
    assert raw_prefix not in serialized
    assert raw_suffix not in serialized
    assert "PatchOps marker contract sample only" not in serialized


def test_live_extractor_blocks_clipboard_without_markers_and_does_not_stage(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: "RAW_UNMARKED_TEXT_SENTINEL",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_INVALID
    assert result["staged_script"] is None
    assert result["contract_result"]["result_label"] == "BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID"
    assert "RAW_UNMARKED_TEXT_SENTINEL" not in json.dumps(result)


def test_live_extractor_blocks_multiple_markers_and_does_not_stage(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    copied = build_example_payload("one") + "\n" + build_example_payload("two")
    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: copied,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_INVALID
    assert result["staged_script"] is None
    assert any("exactly one" in issue for issue in result["contract_result"]["issues"])


def test_live_extractor_blocks_missing_strict_mode(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    copied = build_example_payload("missing_strict").replace("Set-StrictMode -Version Latest", "Write-Host no strict")
    result = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: copied,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_INVALID
    assert result["staged_script"] is None


def test_live_extractor_handles_empty_too_large_and_unavailable_clipboard(tmp_path: Path):
    repo_root, config_path = _repo_with_browser_config(tmp_path)
    empty = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence_empty",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=lambda: "",
    )
    assert empty["ok"] is True
    assert empty["result_label"] == BLOCKED_SCRIPT_EXTRACTION_EMPTY

    too_large = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence_large",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        max_chars=5,
        clipboard_provider=lambda: "x" * 10,
    )
    assert too_large["ok"] is True
    assert too_large["result_label"] == BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE

    def fail_provider():
        raise RuntimeError("clipboard unavailable in test")

    unavailable = run_copied_script_extractor(
        repo_root=repo_root,
        browser_config_path=config_path,
        evidence_root=repo_root / "evidence_unavailable",
        live_clipboard=True,
        confirm_clipboard_text=CLIPBOARD_CONFIRM_TEXT,
        clipboard_provider=fail_provider,
    )
    assert unavailable["ok"] is True
    assert unavailable["result_label"] == BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE


def test_stage_extracted_script_writes_metadata_without_authorizing_run(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_text = "& {\n    Set-StrictMode -Version Latest\n}\n"
    payload_text = f"{SCRIPT_BEGIN}\nname: x\ntype: patchops_powershell_script\nrequires_confirmation: PATCHOPS_CONFIRM_RUN\n\n{script_text}{SCRIPT_END}"
    staged = stage_extracted_script(
        repo_root=repo_root,
        script_text=script_text,
        payload_text=payload_text,
        contract_result={"result_label": "PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED"},
    )
    metadata = json.loads(Path(staged["metadata_path"]).read_text(encoding="utf-8"))
    assert metadata["run_authorized"] is False
    assert metadata["script_executed"] is False
    assert metadata["patchops_invoked"] is False
    assert metadata["script_sha256"] == sha256_text(script_text)


def test_repository_copied_script_extractor_non_live_doctor_is_controlled():
    result = run_copied_script_extractor(
        repo_root=Path.cwd(),
        browser_config_path="data/config/copilot_downloader_browser_target.json",
        evidence_root="data/runtime/copilot_downloader/d2_02_copied_script_extractor_test",
        live_clipboard=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED
    assert result["checks"]["script_not_executed"] is True
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True
    assert result["safety"]["clipboard_read"] is False