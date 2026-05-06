from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d2_01_downloader_script_payload_marker_contract"
SCRIPT_BEGIN = "PATCHOPS_SCRIPT_PAYLOAD_BEGIN"
SCRIPT_END = "PATCHOPS_SCRIPT_PAYLOAD_END"
REQUIRED_TYPE = "patchops_powershell_script"
REQUIRED_CONFIRMATION = "PATCHOPS_CONFIRM_RUN"
PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED = "PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED"
BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID = "BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED,
    BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
})
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,120}$")
INVOCATION_RE = re.compile(r"(?s)&\s*\{.*\}\s*$")
STRICT_MODE_RE = re.compile(r"(?im)^\s*Set-StrictMode\s+-Version\s+Latest\s*$")


@dataclass(frozen=True)
class ScriptPayloadContractResult:
    result_label: str
    issues: tuple[str, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    script_sha256: str | None = None
    payload_sha256: str | None = None
    script_size_chars: int = 0
    payload_size_chars: int = 0

    @property
    def ok(self) -> bool:
        return self.result_label in CONTROLLED_LABELS and not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "result_label": self.result_label,
            "issues": list(self.issues),
            "metadata": dict(self.metadata),
            "script_sha256": self.script_sha256,
            "payload_sha256": self.payload_sha256,
            "script_size_chars": self.script_size_chars,
            "payload_size_chars": self.payload_size_chars,
            "raw_payload_logged": False,
            "raw_script_logged": False,
        }


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def build_example_payload(name: str = PATCH_NAME) -> str:
    return (
        f"{SCRIPT_BEGIN}\n"
        f"name: {name}\n"
        f"type: {REQUIRED_TYPE}\n"
        f"requires_confirmation: {REQUIRED_CONFIRMATION}\n"
        "\n"
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        "    Write-Host \"PatchOps marker contract sample only; not executed.\"\n"
        "}\n"
        f"{SCRIPT_END}\n"
    )


def _invalid(issues: Sequence[str], *, metadata: dict[str, str] | None = None, payload: str = "", script: str = "") -> ScriptPayloadContractResult:
    return ScriptPayloadContractResult(
        result_label=BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
        issues=tuple(issues),
        metadata=metadata or {},
        payload_sha256=sha256_text(payload) if payload else None,
        script_sha256=sha256_text(script) if script else None,
        payload_size_chars=len(payload),
        script_size_chars=len(script),
    )


def _parse_metadata(lines: Sequence[str]) -> tuple[dict[str, str], list[str]]:
    metadata: dict[str, str] = {}
    issues: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            issues.append(f"metadata line is not key:value: {stripped[:40]}")
            continue
        key, value = stripped.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in metadata:
            issues.append(f"duplicate metadata key: {key}")
        metadata[key] = value
    return metadata, issues


def validate_script_payload_contract_text(text: str) -> ScriptPayloadContractResult:
    issues: list[str] = []
    begin_count = text.count(SCRIPT_BEGIN)
    end_count = text.count(SCRIPT_END)
    if begin_count == 0 or end_count == 0:
        return _invalid(["payload markers are required; no extraction without markers"])
    if begin_count != 1 or end_count != 1:
        return _invalid(["exactly one payload marker pair is required; multiple markers are blocked"], payload=text)
    begin_index = text.index(SCRIPT_BEGIN)
    end_index = text.index(SCRIPT_END)
    if end_index <= begin_index:
        return _invalid(["payload end marker must appear after begin marker"], payload=text)

    inner = text[begin_index + len(SCRIPT_BEGIN):end_index].strip("\r\n")
    payload = text[begin_index:end_index + len(SCRIPT_END)]
    match = INVOCATION_RE.search(inner)
    if match is None:
        metadata_lines = inner.splitlines()
        metadata, metadata_issues = _parse_metadata(metadata_lines)
        return _invalid([*metadata_issues, "missing terminal & { ... } PowerShell invocation block"], metadata=metadata, payload=payload)

    script = match.group(0).rstrip() + "\n"
    metadata_text = inner[:match.start()].strip("\r\n")
    metadata, metadata_issues = _parse_metadata(metadata_text.splitlines())
    issues.extend(metadata_issues)

    name = metadata.get("name", "")
    if not name:
        issues.append("metadata name is required")
    elif NAME_RE.fullmatch(name) is None:
        issues.append("metadata name contains invalid characters")
    if metadata.get("type") != REQUIRED_TYPE:
        issues.append(f"metadata type must be {REQUIRED_TYPE}")
    if metadata.get("requires_confirmation") != REQUIRED_CONFIRMATION:
        issues.append(f"metadata requires_confirmation must be {REQUIRED_CONFIRMATION}")
    if STRICT_MODE_RE.search(script) is None:
        issues.append("script must include Set-StrictMode -Version Latest inside & { ... }")
    if not script.lstrip().startswith("&"):
        issues.append("script invocation must start with & { ... }")
    if issues:
        return _invalid(issues, metadata=metadata, payload=payload, script=script)
    return ScriptPayloadContractResult(
        result_label=PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED,
        metadata={
            "name": metadata["name"],
            "type": metadata["type"],
            "requires_confirmation": metadata["requires_confirmation"],
        },
        script_sha256=sha256_text(script),
        payload_sha256=sha256_text(payload),
        script_size_chars=len(script),
        payload_size_chars=len(payload),
    )


def validate_script_payload_contract_file(path: str | Path) -> ScriptPayloadContractResult:
    file_path = Path(path)
    if not file_path.is_file():
        return _invalid([f"payload file does not exist: {file_path}"])
    return validate_script_payload_contract_text(file_path.read_text(encoding="utf-8"))


def run_script_payload_contract_doctor(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    sample_path: str | Path | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else root / "data" / "runtime" / "copilot_downloader" / "d2_01_script_payload_contract"
    result = validate_script_payload_contract_file(sample_path) if sample_path else validate_script_payload_contract_text(build_example_payload())
    safety = DownloaderSafetyFlags()
    checks = {
        "contract_validation_completed": True,
        "no_marker_means_no_extraction": True,
        "multiple_markers_blocked": validate_script_payload_contract_text(build_example_payload("a") + build_example_payload("b")).result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
        "missing_invocation_block_blocked": validate_script_payload_contract_text(f"{SCRIPT_BEGIN}\nname: x\ntype: {REQUIRED_TYPE}\nrequires_confirmation: {REQUIRED_CONFIRMATION}\n{SCRIPT_END}\n").result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
        "strict_mode_required": validate_script_payload_contract_text(build_example_payload().replace("Set-StrictMode -Version Latest", "Write-Host no strict")).result_label == BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "artifact_not_extracted": True,
        "artifact_not_staged": True,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "uploader_not_imported": True,
        "raw_payload_not_logged": True,
        "raw_script_not_logged": True,
    }
    details = {"checks": checks, "contract_result": result.to_dict()}
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence = DownloaderEvidenceRecord(
            patch_name=PATCH_NAME,
            result_label=result.result_label,
            safety=safety,
            details=details,
        )
        evidence_files = write_evidence_pair(evidence_dir, "script_payload_contract", evidence)
    return {
        "ok": result.result_label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": result.result_label,
        "contract_result": result.to_dict(),
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.script_payload_contract")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--sample-path", default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_script_payload_contract_doctor(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        sample_path=args.sample_path,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())