from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.merge_readiness_audit import (
    FAIL_MERGE_NOT_READY,
    PASS_MERGE_READY,
    scan_downloader_manifests_for_uploader_owned_paths,
    scan_for_forbidden_uploader_imports,
    run_merge_readiness_audit,
    validate_handoff_file_contract,
)


def _write_handoff(root: Path, *, uploader_ready: bool = False, result: str = "FAIL", exit_code: int | None = 1) -> Path:
    handoff_dir = root / "data" / "runtime" / "copilot_handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "handoff_contract": "file_only_no_uploader_import",
        "status": "PASS_HANDOFF_WRITTEN" if uploader_ready else "FAIL_HANDOFF_WRITE",
        "artifact_kind": "patchops_bundle_zip",
        "artifact_sha256": "abc123",
        "canonical_report_path": str(root / "report.txt"),
        "canonical_report_sha256": "f" * 64 if uploader_ready else None,
        "canonical_report_exists": uploader_ready,
        "canonical_report_sha256_matches": uploader_ready,
        "result": result,
        "exit_code": exit_code,
        "uploader_ready": uploader_ready,
        "safety": {
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "cloudflare_bypass_attempted": False,
            "captcha_bypass_attempted": False,
            "chatgpt_submit_performed": False,
            "file_upload_attempted": False,
            "canonical_report_found": uploader_ready,
        },
    }
    json_path = handoff_dir / "latest_report_handoff.json"
    text_path = handoff_dir / "latest_report_handoff.txt"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text_path.write_text("PATCHOPS DOWNLOADER REPORT HANDOFF\n", encoding="utf-8")
    return json_path


def test_merge_readiness_import_scan_detects_forbidden_uploader_import(tmp_path: Path):
    src = tmp_path / "patchops" / "copilot_downloader"
    src.mkdir(parents=True)
    bad = src / "bad.py"
    bad.write_text("from patchops.chatgpt_uploader import runner\n", encoding="utf-8")
    result = scan_for_forbidden_uploader_imports(tmp_path, files=[bad])
    assert result["ok"] is False
    assert result["violation_count"] == 1
    assert result["violations"][0]["forbidden"] == "patchops.chatgpt_uploader"


def test_merge_readiness_import_scan_allows_downloader_only_imports(tmp_path: Path):
    src = tmp_path / "patchops" / "copilot_downloader"
    src.mkdir(parents=True)
    good = src / "good.py"
    good.write_text("from patchops.copilot_downloader.models import DownloaderSafetyFlags\n", encoding="utf-8")
    result = scan_for_forbidden_uploader_imports(tmp_path, files=[good])
    assert result["ok"] is True
    assert result["violation_count"] == 0


def test_merge_readiness_path_scan_detects_uploader_owned_path_in_downloader_manifest(tmp_path: Path):
    manifest = tmp_path / "data" / "runtime" / "direct_patches" / "bad_downloader" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "patch_name": "bad_downloader_patch",
                "tags": ["copilot-downloader"],
                "files_to_write": [{"path": "patchops/chatgpt_uploader/bad.py", "content_path": "x"}],
            }
        ),
        encoding="utf-8",
    )
    result = scan_downloader_manifests_for_uploader_owned_paths(tmp_path, manifests=[manifest])
    assert result["ok"] is False
    assert result["violation_count"] == 1


def test_merge_readiness_path_scan_allows_downloader_owned_paths(tmp_path: Path):
    manifest = tmp_path / "data" / "runtime" / "direct_patches" / "good_downloader" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "patch_name": "good_downloader_patch",
                "tags": ["copilot-downloader"],
                "files_to_write": [{"path": "patchops/copilot_downloader/good.py", "content_path": "x"}],
            }
        ),
        encoding="utf-8",
    )
    result = scan_downloader_manifests_for_uploader_owned_paths(tmp_path, manifests=[manifest])
    assert result["ok"] is True
    assert result["violation_count"] == 0


def test_handoff_file_contract_accepts_not_ready_file_contract(tmp_path: Path):
    json_path = _write_handoff(tmp_path, uploader_ready=False, result="PASS", exit_code=0)
    result = validate_handoff_file_contract(tmp_path, handoff_json=json_path)
    assert result["ok"] is True
    assert result["handoff_json_exists"] is True
    assert result["handoff_text_exists"] is True
    assert result["handoff_contract"] == "file_only_no_uploader_import"
    assert result["uploader_ready"] is False


def test_handoff_file_contract_rejects_ready_without_valid_report(tmp_path: Path):
    json_path = _write_handoff(tmp_path, uploader_ready=True, result="FAIL", exit_code=7)
    result = validate_handoff_file_contract(tmp_path, handoff_json=json_path)
    assert result["ok"] is False
    assert any("PASS" in issue for issue in result["issues"])


def test_merge_readiness_audit_passes_with_valid_independent_downloader_contract(tmp_path: Path):
    src = tmp_path / "patchops" / "copilot_downloader"
    src.mkdir(parents=True)
    (src / "good.py").write_text("from pathlib import Path\n", encoding="utf-8")
    manifest = tmp_path / "data" / "runtime" / "direct_patches" / "good_downloader" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"patch_name": "good_downloader_patch", "tags": ["copilot-downloader"], "files_to_write": [{"path": "patchops/copilot_downloader/good.py"}]}), encoding="utf-8")
    handoff = _write_handoff(tmp_path, uploader_ready=False, result="PASS", exit_code=0)
    result = run_merge_readiness_audit(repo_root=tmp_path, output_dir=tmp_path / "reports", evidence_root=tmp_path / "evidence", handoff_json=handoff)
    assert result["ok"] is True
    assert result["result_label"] == PASS_MERGE_READY
    assert result["merge_ready"] is True
    assert result["checks"]["no_uploader_imports"] is True
    assert result["checks"]["no_uploader_owned_paths_touched"] is True
    assert result["checks"]["handoff_contract_file_based"] is True
    assert Path(result["report_paths"]["json"]).is_file()
    assert Path(result["report_paths"]["latest_text"]).is_file()
    assert Path(result["evidence_files"]["json"]).is_file()


def test_merge_readiness_audit_blocks_when_handoff_missing(tmp_path: Path):
    src = tmp_path / "patchops" / "copilot_downloader"
    src.mkdir(parents=True)
    (src / "good.py").write_text("from pathlib import Path\n", encoding="utf-8")
    result = run_merge_readiness_audit(repo_root=tmp_path, output_dir=tmp_path / "reports", evidence_root=tmp_path / "evidence", handoff_json=tmp_path / "missing.json")
    assert result["ok"] is False
    assert result["result_label"] == FAIL_MERGE_NOT_READY
    assert result["merge_ready"] is False
    assert any("handoff" in issue for issue in result["issues"])


def test_repository_merge_readiness_audit_doctor_is_controlled():
    result = run_merge_readiness_audit(
        repo_root=Path.cwd(),
        output_dir="data/runtime/copilot_downloader/m0_01_merge_readiness_audit_test",
        evidence_root="data/runtime/copilot_downloader/m0_01_merge_readiness_audit_test_evidence",
        handoff_json="data/runtime/copilot_handoff/latest_report_handoff.json",
    )
    assert result["result_label"] in {PASS_MERGE_READY, FAIL_MERGE_NOT_READY}
    assert result["checks"]["browser_not_started"] is True
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["artifact_not_executed"] is True
    assert result["checks"]["uploader_not_called"] is True
    assert Path(result["report_paths"]["text"]).is_file()