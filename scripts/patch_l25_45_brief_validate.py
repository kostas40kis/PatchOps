from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_download_artifact_controlled_run_package_proof as proof


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:5000])
        raise AssertionError(message)


def _forbidden_import_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    forbidden = {"selenium", "webdriver_manager", "pyperclip", "psutil"}
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in forbidden:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".", 1)[0] in forbidden:
                hits.append(node.module or "")
    return sorted(set(hits))


def _source_l25_44_payload() -> dict[str, Any]:
    return {
        "ok": True,
        "patch": "L25.44",
        "package_execution_dry_run_final_acceptance_marker": True,
        "package_execution_dry_run_ladder_final_acceptance": True,
        "package_execution_dry_run_final_acceptance_from_source_payload_only": True,
        "accepted_l25_41_package_execution_authorization_gate": True,
        "accepted_l25_42_package_execution_dry_run_proof": True,
        "accepted_l25_43_package_execution_dry_run_broad_checkpoint": True,
        "accepted_package_execution_dry_run_only": True,
        "accepted_package_execution_dry_run_allowed": True,
        "accepted_candidate_artifact_suffix_zip": True,
        "accepted_candidate_artifact_under_l25_42_runtime": True,
        "accepted_would_run_command_rendered": True,
        "accepted_would_run_command_program": "py",
        "accepted_would_invoke_patchops_run_package_in_future_patch": True,
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": True,
        "accepted_broad_checkpoint_rejects_source_that_invoked_run_package": True,
        "final_marker_rejects_source_that_invoked_run_package": True,
        "artifact_path_opened_by_l25_44": False,
        "artifact_bytes_read_by_l25_44": False,
        "zip_member_opened_by_l25_44": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "browser_started": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "pasteback": False,
    }


def _artifact_under_l25_45_runtime(root: Path, artifact_path: Path) -> bool:
    try:
        base = (root / "data" / "runtime" / "browser_downloads" / "l25_45_controlled_run_package").resolve()
        return str(artifact_path.resolve()).startswith(str(base))
    except OSError:
        return False


def _write_controlled_package(root: Path) -> Path:
    artifact_path = root / proof.DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    launcher = """param(\n    [string]$WrapperRoot = ''\n)\n$ErrorActionPreference = 'Stop'\nWrite-Host 'PATCHOPS_L25_45_CONTROLLED_RUN_PACKAGE_MARKER'\nWrite-Host 'CONTROLLED_PACKAGE_WRITES_TO_TARGET:false'\nWrite-Host 'CONTROLLED_PACKAGE_BROWSER_STARTED:false'\nWrite-Host 'CONTROLLED_PACKAGE_PASTEBACK:false'\nWrite-Host ('CONTROLLED_PACKAGE_WRAPPER_ROOT:' + $WrapperRoot)\nexit 0\n"""
    manifest = {
        "manifest_version": "1",
        "patch_name": "l25_45_controlled_no_write_runtime_package",
        "active_profile": "generic_python",
        "target_project_root": str(root),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
    }
    metadata = {
        "schema_version": "1",
        "patch_name": "l25_45_controlled_no_write_runtime_package",
        "bundle_mode": "controlled_run_package_no_write_proof",
        "launcher_path": "run_with_patchops.ps1",
        "manifest_path": "manifest.json",
        "content_root": "content",
    }
    with zipfile.ZipFile(artifact_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("run_with_patchops.ps1", launcher)
        archive.writestr("bundle_meta.json", json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
        archive.writestr("README.txt", "L25.45 controlled no-write run-package proof artifact.\n")
        archive.writestr("content/.keep", "controlled artifact marker\n")
    return artifact_path


def _run_controlled_package(root: Path, artifact_path: Path) -> dict[str, Any]:
    args = ["-m", "patchops.cli", "run-package", str(artifact_path), "--wrapper-root", str(root)]
    command_text = "py " + " ".join('"' + item + '"' if " " in item else item for item in args)
    try:
        completed = subprocess.run(
            ["py", *args],
            cwd=str(root),
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        return {
            "invoked": True,
            "exit_code": int(completed.returncode),
            "timed_out": False,
            "command_program": "py",
            "command_args": args,
            "command_text": command_text,
            "artifact_path": str(artifact_path),
            "artifact_under_l25_45_runtime": _artifact_under_l25_45_runtime(root, artifact_path),
            "artifact_suffix_zip": artifact_path.suffix.lower() == ".zip",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "invoked": True,
            "exit_code": 124,
            "timed_out": True,
            "command_program": "py",
            "command_args": args,
            "command_text": command_text,
            "artifact_path": str(artifact_path),
            "artifact_under_l25_45_runtime": _artifact_under_l25_45_runtime(root, artifact_path),
            "artifact_suffix_zip": artifact_path.suffix.lower() == ".zip",
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\nTIMEOUT after 180 seconds",
        }


def _validate_payload(payload: dict[str, Any]) -> None:
    _assert(payload.get("ok") is True, "payload is not ok", payload)
    _assert(payload.get("patch") == "L25.45", "wrong patch marker", payload)
    _assert(payload.get("controlled_run_package_first_proof") is True, "controlled proof marker missing", payload)
    _assert(payload.get("controlled_run_package_pass_detection_repaired_by_l25_45a") is True, "L25.45A repair marker missing", payload)
    _assert(payload.get("controlled_run_package_proof_from_l25_44_final_acceptance") is True, "L25.44 source proof missing", payload)
    _assert(payload.get("controlled_artifact_under_l25_45_runtime") is True, "artifact path guard missing", payload)
    _assert(payload.get("controlled_artifact_suffix_zip") is True, "artifact suffix guard missing", payload)
    _assert(payload.get("controlled_run_package_invoked") is True, "run-package invocation missing", payload)
    _assert(payload.get("controlled_run_package_exit_code") == 0, "run-package exit must be zero", payload)
    _assert(payload.get("controlled_run_package_timed_out") is False, "run-package timed out", payload)
    _assert(payload.get("controlled_run_package_result_pass") is True, "run-package PASS missing", payload)
    _assert(payload.get("controlled_run_package_exit_zero_plus_marker_pass_observed") is True, "exit-zero plus marker PASS missing", payload)
    _assert(payload.get("controlled_run_package_marker_observed") is True, "controlled marker missing", payload)
    _assert(payload.get("controlled_package_target_write_marker_false") is True, "target-write false marker missing", payload)
    _assert(payload.get("controlled_package_browser_marker_false") is True, "browser false marker missing", payload)
    _assert(payload.get("controlled_package_pasteback_marker_false") is True, "pasteback false marker missing", payload)
    _assert(payload.get("package_execution_allowed") is True, "package execution should be allowed for controlled proof", payload)
    _assert(payload.get("controlled_package_run_performed_by_validator") is True, "validator run marker missing", payload)
    _assert(payload.get("package_run") is True, "package run marker missing", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_controlled_artifact") is True, "controlled run-package marker missing", payload)
    _assert(payload.get("patchops_cli_run_package_invoked_for_real_artifact") is True, "real-artifact run-package marker missing", payload)
    _assert(payload.get("real_archive_candidate_extracted") is True, "PatchOps runtime extraction marker missing", payload)
    _assert(payload.get("adapter_archive_extraction_performed") is False, "adapter extraction must remain false", payload)
    _assert(payload.get("archive_member_extracted_to_project") is False, "target extraction must remain false", payload)
    _assert(payload.get("artifact_member_written_to_project") is False, "artifact target write must remain false", payload)
    _assert(payload.get("target_project_file_write_performed_by_controlled_package") is False, "controlled package must not write target files", payload)
    _assert(payload.get("browser_started") is False, "browser must not start", payload)
    _assert(payload.get("pasteback_workflow_active") is False, "pasteback must remain false", payload)
    _assert(payload.get("git_commit_performed") is False, "git commit must remain false", payload)
    _assert(payload.get("git_push_performed") is False, "git push must remain false", payload)


def _validate_exit_zero_marker_regression(root: Path) -> None:
    source = _source_l25_44_payload()
    run_payload = {
        "invoked": True,
        "exit_code": 0,
        "timed_out": False,
        "command_program": "py",
        "command_args": ["-m", "patchops.cli", "run-package", str(root / proof.DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH), "--wrapper-root", str(root)],
        "command_text": "py -m patchops.cli run-package <controlled> --wrapper-root <repo>",
        "artifact_path": str(root / proof.DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH),
        "artifact_under_l25_45_runtime": True,
        "artifact_suffix_zip": True,
        "stdout": "PATCHOPS_L25_45_CONTROLLED_RUN_PACKAGE_MARKER\nCONTROLLED_PACKAGE_WRITES_TO_TARGET:false\nCONTROLLED_PACKAGE_BROWSER_STARTED:false\nCONTROLLED_PACKAGE_PASTEBACK:false\n",
        "stderr": "",
    }
    payload = proof.build_real_download_artifact_controlled_run_package_proof(root, source_payload=source, run_payload=run_payload)
    _assert(payload.get("ok") is True, "exit-zero plus marker regression must pass", payload)
    _assert(payload.get("controlled_run_package_textual_pass_observed") is False, "regression fixture should not rely on textual PASS", payload)
    _assert(payload.get("controlled_run_package_exit_zero_plus_marker_pass_observed") is True, "exit-zero plus marker marker missing", payload)


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    artifact_path = _write_controlled_package(root)
    source = _source_l25_44_payload()
    run_payload = _run_controlled_package(root, artifact_path)
    payload = proof.build_real_download_artifact_controlled_run_package_proof(
        root,
        source_payload=source,
        run_payload=run_payload,
    )
    _validate_payload(payload)
    _validate_exit_zero_marker_regression(root)

    default_payload = proof.build_real_download_artifact_controlled_run_package_proof(root, source_payload=source)
    _assert(default_payload.get("ok") is False, "default without run payload must fail", default_payload)

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_download_artifact_controlled_run_package_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_download_artifact_controlled_run_package_proof.md"
    module_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    _assert(not _forbidden_import_hits(module_text), "forbidden browser imports in L25.45 module", payload)
    _assert("L25.45A repaired the PASS detection" in doc_text, "doc missing L25.45A repair wording", payload)
    _assert("first controlled PatchOps `run-package` proof" in doc_text, "doc missing controlled run-package wording", payload)
    _assert("No controlled package target project write" in doc_text, "doc missing no target write boundary", payload)
    _assert("No package execution by the browser adapter" in doc_text, "doc missing no adapter execution boundary", payload)

    return {
        "ok": True,
        "patch": "L25.45A",
        "repaired_patch": "L25.45",
        "controlled_artifact_path": payload.get("controlled_artifact_path"),
        "controlled_run_package_first_proof": payload.get("controlled_run_package_first_proof"),
        "controlled_run_package_pass_detection_repaired_by_l25_45a": payload.get("controlled_run_package_pass_detection_repaired_by_l25_45a"),
        "controlled_run_package_proof_from_l25_44_final_acceptance": payload.get("controlled_run_package_proof_from_l25_44_final_acceptance"),
        "controlled_artifact_under_l25_45_runtime": payload.get("controlled_artifact_under_l25_45_runtime"),
        "controlled_artifact_suffix_zip": payload.get("controlled_artifact_suffix_zip"),
        "controlled_run_package_invoked": payload.get("controlled_run_package_invoked"),
        "controlled_run_package_exit_code": payload.get("controlled_run_package_exit_code"),
        "controlled_run_package_result_pass": payload.get("controlled_run_package_result_pass"),
        "controlled_run_package_exit_zero_plus_marker_pass_observed": payload.get("controlled_run_package_exit_zero_plus_marker_pass_observed"),
        "controlled_run_package_marker_observed": payload.get("controlled_run_package_marker_observed"),
        "controlled_package_target_write_marker_false": payload.get("controlled_package_target_write_marker_false"),
        "controlled_package_browser_marker_false": payload.get("controlled_package_browser_marker_false"),
        "controlled_package_pasteback_marker_false": payload.get("controlled_package_pasteback_marker_false"),
        "exit_zero_plus_marker_regression_passed": True,
        "default_without_run_payload_rejected": default_payload.get("ok") is False,
        "package_execution_allowed": payload.get("package_execution_allowed"),
        "controlled_package_run_performed_by_validator": payload.get("controlled_package_run_performed_by_validator"),
        "package_run": payload.get("package_run"),
        "patchops_cli_run_package_invoked_for_controlled_artifact": payload.get("patchops_cli_run_package_invoked_for_controlled_artifact"),
        "patchops_cli_run_package_invoked_for_real_artifact": payload.get("patchops_cli_run_package_invoked_for_real_artifact"),
        "real_archive_candidate_extracted": payload.get("real_archive_candidate_extracted"),
        "adapter_archive_extraction_performed": payload.get("adapter_archive_extraction_performed"),
        "archive_member_extracted_to_project": payload.get("archive_member_extracted_to_project"),
        "artifact_member_written_to_project": payload.get("artifact_member_written_to_project"),
        "target_project_file_write_performed_by_controlled_package": payload.get("target_project_file_write_performed_by_controlled_package"),
        "browser_started": payload.get("browser_started"),
        "pasteback": payload.get("pasteback_workflow_active"),
        "git_commit_performed": payload.get("git_commit_performed"),
        "git_push_performed": payload.get("git_push_performed"),
        "next_patch": payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.45A brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
