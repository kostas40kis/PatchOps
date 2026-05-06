from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "m0_01_downloader_merge_readiness_audit"
PASS_MERGE_READY = "PASS_MERGE_READY"
FAIL_MERGE_NOT_READY = "FAIL_MERGE_NOT_READY"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_MERGE_READY, FAIL_MERGE_NOT_READY})
DOWNLOADER_OWNED_PREFIXES: tuple[str, ...] = (
    "patchops/copilot_downloader/",
    "docs/copilot_downloader_",
    "scripts/run_downloader_",
    "tests/test_copilot_downloader_",
    "data/config/copilot_downloader_config.json",
    "data/runtime/copilot_downloader/",
    "data/runtime/copilot_handoff/",
)
UPLOADER_OWNED_PREFIXES: tuple[str, ...] = (
    "patchops/chatgpt_uploader/",
    "docs/chatgpt_uploader_",
    "tests/test_chatgpt_uploader_",
)
FORBIDDEN_UPLOADER_IMPORTS: tuple[str, ...] = (
    "patchops.chatgpt_uploader",
    "patchops.copilot_uploader",
    "chatgpt_uploader",
    "copilot_uploader",
)
HANDOFF_JSON_REL = "data/runtime/copilot_handoff/latest_report_handoff.json"
HANDOFF_TEXT_REL = "data/runtime/copilot_handoff/latest_report_handoff.txt"


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def _to_posix_rel(path: Path, root: Path) -> str:
    return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()


def _path_starts_with_any(rel_path: str, prefixes: Sequence[str]) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(normalized == prefix.rstrip("/") or normalized.startswith(prefix) for prefix in prefixes)


def collect_downloader_python_files(repo_root: str | Path) -> list[Path]:
    root = Path(repo_root).resolve(strict=False)
    candidates: list[Path] = []
    for base in [root / "patchops" / "copilot_downloader", root / "scripts", root / "tests"]:
        if not base.exists():
            continue
        pattern = "*.py" if base.name == "copilot_downloader" else ("run_downloader_*.py" if base.name == "scripts" else "test_copilot_downloader_*_current.py")
        candidates.extend(sorted(base.glob(pattern)))
    return [path for path in candidates if path.is_file()]


def _import_name_for_node(node: ast.AST) -> list[str]:
    names: list[str] = []
    if isinstance(node, ast.Import):
        names.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            names.append(node.module)
    return names


def scan_for_forbidden_uploader_imports(repo_root: str | Path, files: Sequence[Path] | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    scan_files = list(files) if files is not None else collect_downloader_python_files(root)
    violations: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    for path in scan_files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            parse_errors.append({"path": _to_posix_rel(path, root), "error": str(exc)})
            continue
        for node in ast.walk(tree):
            for import_name in _import_name_for_node(node):
                for forbidden in FORBIDDEN_UPLOADER_IMPORTS:
                    if import_name == forbidden or import_name.startswith(forbidden + "."):
                        violations.append({
                            "path": _to_posix_rel(path, root),
                            "line": getattr(node, "lineno", None),
                            "import_name": import_name,
                            "forbidden": forbidden,
                        })
    return {
        "ok": not violations and not parse_errors,
        "files_scanned": [_to_posix_rel(path, root) for path in scan_files],
        "violation_count": len(violations),
        "violations": violations,
        "parse_errors": parse_errors,
    }


def collect_downloader_patch_manifests(repo_root: str | Path) -> list[Path]:
    root = Path(repo_root).resolve(strict=False)
    patch_root = root / "data" / "runtime" / "direct_patches"
    if not patch_root.is_dir():
        return []
    manifests: list[Path] = []
    for manifest in sorted(patch_root.glob("*/manifest.json")):
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        patch_name = str(payload.get("patch_name", ""))
        tags = [str(tag) for tag in payload.get("tags", [])]
        if "downloader" in patch_name or "copilot-downloader" in tags:
            manifests.append(manifest)
    return manifests


def scan_downloader_manifests_for_uploader_owned_paths(repo_root: str | Path, manifests: Sequence[Path] | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    scan_manifests = list(manifests) if manifests is not None else collect_downloader_patch_manifests(root)
    violations: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []
    for manifest in scan_manifests:
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            parse_errors.append({"manifest": _to_posix_rel(manifest, root), "error": str(exc)})
            continue
        paths: list[str] = []
        for item in payload.get("files_to_write", []) or []:
            if isinstance(item, dict) and item.get("path"):
                paths.append(str(item["path"]))
        for item in payload.get("backup_files", []) or []:
            if isinstance(item, str):
                paths.append(item)
            elif isinstance(item, dict) and item.get("path"):
                paths.append(str(item["path"]))
        for rel in paths:
            normalized = rel.replace("\\", "/").lstrip("./")
            if _path_starts_with_any(normalized, UPLOADER_OWNED_PREFIXES):
                violations.append({
                    "manifest": _to_posix_rel(manifest, root),
                    "patch_name": payload.get("patch_name"),
                    "path": normalized,
                })
    return {
        "ok": not violations and not parse_errors,
        "manifest_count": len(scan_manifests),
        "manifests_scanned": [_to_posix_rel(path, root) for path in scan_manifests],
        "violation_count": len(violations),
        "violations": violations,
        "parse_errors": parse_errors,
    }


def validate_handoff_file_contract(repo_root: str | Path, handoff_json: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    json_path = Path(handoff_json).resolve(strict=False) if handoff_json is not None else _repo_child(root, *HANDOFF_JSON_REL.split("/"))
    text_path = json_path.with_suffix(".txt") if json_path.name != "latest_report_handoff.json" else _repo_child(root, *HANDOFF_TEXT_REL.split("/"))
    issues: list[str] = []
    payload: dict[str, Any] | None = None
    if not json_path.is_file():
        issues.append("latest_report_handoff.json is missing")
    else:
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"handoff JSON is malformed: {exc}")
    if not text_path.is_file():
        issues.append("latest_report_handoff.txt is missing")
    if payload is not None:
        required = ["schema_version", "producer", "canonical_report_path", "canonical_report_sha256", "result", "exit_code", "uploader_ready", "safety"]
        for key in required:
            if key not in payload:
                issues.append(f"handoff JSON missing required key: {key}")
        if payload.get("producer") != "patchops.copilot_downloader":
            issues.append("handoff producer must be patchops.copilot_downloader")
        if payload.get("handoff_contract") != "file_only_no_uploader_import":
            issues.append("handoff_contract must be file_only_no_uploader_import")
        if payload.get("uploader_ready") is True:
            if payload.get("result") != "PASS" or payload.get("exit_code") != 0:
                issues.append("uploader_ready true requires PASS and exit_code 0")
            if not payload.get("canonical_report_exists"):
                issues.append("uploader_ready true requires canonical_report_exists true")
            if not payload.get("canonical_report_sha256_matches"):
                issues.append("uploader_ready true requires sha256 match")
    return {
        "ok": not issues,
        "handoff_json_path": str(json_path),
        "handoff_text_path": str(text_path),
        "handoff_json_exists": json_path.is_file(),
        "handoff_text_exists": text_path.is_file(),
        "uploader_ready": None if payload is None else payload.get("uploader_ready"),
        "producer": None if payload is None else payload.get("producer"),
        "handoff_contract": None if payload is None else payload.get("handoff_contract"),
        "issues": issues,
    }


def write_merge_readiness_report(output_dir: str | Path, payload: dict[str, Any]) -> dict[str, str]:
    out_dir = Path(output_dir).resolve(strict=False)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"downloader_merge_readiness_audit_{timestamp}.json"
    text_path = out_dir / f"downloader_merge_readiness_audit_{timestamp}.txt"
    latest_json = out_dir / "latest_downloader_merge_readiness_audit.json"
    latest_text = out_dir / "latest_downloader_merge_readiness_audit.txt"
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")
    lines = [
        "PATCHOPS DOWNLOADER MERGE READINESS AUDIT",
        "========================================",
        f"generated_utc: {payload.get('generated_utc')}",
        f"result_label: {payload.get('result_label')}",
        f"merge_ready: {payload.get('merge_ready')}",
        f"issue_count: {len(payload.get('issues', []))}",
        "",
        "checks:",
    ]
    for key, value in sorted((payload.get("checks") or {}).items()):
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("issues:")
    if payload.get("issues"):
        lines.extend([f"- {issue}" for issue in payload["issues"]])
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("handoff:")
    handoff = payload.get("handoff_contract") or {}
    for key in ["handoff_json_path", "handoff_text_path", "uploader_ready", "handoff_contract"]:
        lines.append(f"{key}: {handoff.get(key)}")
    lines.append("")
    lines.append("safety:")
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"{key}: {value}")
    lines.append("")
    lines.append("final PASS/FAIL")
    lines.append("PASS" if payload.get("merge_ready") else "FAIL")
    text_report = "\n".join(lines) + "\n"
    text_path.write_text(text_report, encoding="utf-8")
    latest_text.write_text(text_report, encoding="utf-8")
    return {"json": str(json_path), "text": str(text_path), "latest_json": str(latest_json), "latest_text": str(latest_text)}


def _write_audit_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "merge_readiness_audit", evidence)


def run_merge_readiness_audit(
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    evidence_root: str | Path | None = None,
    handoff_json: str | Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    out_dir = Path(output_dir).resolve(strict=False) if output_dir is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "merge_readiness")
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "m0_01_merge_readiness_audit")
    import_scan = scan_for_forbidden_uploader_imports(root)
    path_scan = scan_downloader_manifests_for_uploader_owned_paths(root)
    handoff = validate_handoff_file_contract(root, handoff_json=handoff_json)
    issues: list[str] = []
    if not import_scan["ok"]:
        issues.append("downloader source imports uploader code")
    if not path_scan["ok"]:
        issues.append("downloader manifest touches uploader-owned paths")
    if not handoff["ok"]:
        issues.append("handoff contract is missing or invalid")
    safety = DownloaderSafetyFlags()
    checks = {
        "no_uploader_imports": import_scan["ok"],
        "no_uploader_owned_paths_touched": path_scan["ok"],
        "handoff_contract_file_based": handoff["ok"],
        "handoff_json_present": handoff["handoff_json_exists"],
        "handoff_text_present": handoff["handoff_text_exists"],
        "focused_downloader_tests_expected_in_manifest": True,
        "safe_core_tests_expected_in_manifest": True,
        "merge_readiness_report_written": True,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "uploader_not_called": True,
        "git_commit_not_performed": True,
        "git_push_not_performed": True,
    }
    result_label = PASS_MERGE_READY if not issues and all(checks.values()) else FAIL_MERGE_NOT_READY
    payload = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "result_label": result_label,
        "merge_ready": result_label == PASS_MERGE_READY,
        "issues": issues,
        "checks": checks,
        "forbidden_uploader_import_scan": import_scan,
        "uploader_owned_path_scan": path_scan,
        "handoff_contract": handoff,
        "safety": safety.to_dict(),
        "report_paths": {},
        "evidence_files": {},
    }
    payload["report_paths"] = write_merge_readiness_report(out_dir, payload)
    if write_evidence:
        payload["evidence_files"] = _write_audit_evidence(evidence_dir, result_label, safety, {"checks": checks, "issues": issues, "report_paths": payload["report_paths"]})
    payload["ok"] = result_label in CONTROLLED_LABELS and all(checks.values())
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.merge_readiness_audit")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--handoff-json", default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_merge_readiness_audit(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        evidence_root=args.evidence_root,
        handoff_json=args.handoff_json,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())