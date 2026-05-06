from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from patchops.copilot_downloader.classifier import SCRIPT_PAYLOAD_BEGIN, SCRIPT_PAYLOAD_END
from patchops.copilot_downloader.models import ShapeValidationResult

SCRIPT_KIND = "patchops_script_payload"
SCRIPT_PASS_LABEL = "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"
INVALID_LABEL = "BLOCKED_INVALID_ARTIFACT"
EXPLICIT_GIT_WRITE_MARKER = "PATCHOPS_ALLOW_GIT_WRITE"

BANNED_SCRIPT_PATTERNS: tuple[tuple[str, str], ...] = (
    ("encoded_command", r"(?i)-encodedcommand\b|\bencodedcommand\b"),
    ("invoke_expression", r"(?i)\binvoke-expression\b|\biex\b"),
    ("hidden_download", r"(?i)\binvoke-webrequest\b|\biwr\b|\bstart-bitstransfer\b|\bnew-object\s+net\.webclient\b|downloadstring\s*\(|downloadfile\s*\(|\bcurl\b|\bwget\b"),
    ("destructive_remove", r"(?i)\bremove-item\b|\brd\s+/s\b|\brmdir\s+/s\b|\bdel\s+/[fsq]\b|\berase\b"),
    ("system_mutation", r"(?i)\bformat-volume\b|\bclear-disk\b|\bremove-partition\b|\bset-executionpolicy\b|\bdisable-windowsoptionalfeature\b"),
    ("process_or_shell_escape", r"(?i)\bstart-process\b|\bstart-job\b|\binvoke-command\b|\bpsexec\b|\bwmic\b"),
)


def read_script_text(path: str | Path, *, max_bytes: int = 2 * 1024 * 1024) -> str:
    data = Path(path).read_bytes()[:max_bytes]
    return data.decode("utf-8", errors="replace")


def extract_single_marked_payload(text: str) -> tuple[str | None, list[str]]:
    issues: list[str] = []
    begin_count = text.count(SCRIPT_PAYLOAD_BEGIN)
    end_count = text.count(SCRIPT_PAYLOAD_END)
    if begin_count != 1:
        issues.append(f"expected exactly one {SCRIPT_PAYLOAD_BEGIN} marker, found {begin_count}")
    if end_count != 1:
        issues.append(f"expected exactly one {SCRIPT_PAYLOAD_END} marker, found {end_count}")
    if issues:
        return None, issues
    begin_index = text.index(SCRIPT_PAYLOAD_BEGIN) + len(SCRIPT_PAYLOAD_BEGIN)
    end_index = text.index(SCRIPT_PAYLOAD_END)
    if begin_index >= end_index:
        return None, ["payload end marker appears before payload body"]
    return text[begin_index:end_index], []


def _has_invocation_block(payload: str) -> bool:
    return re.search(r"(?s)&\s*\{.*\}\s*$", payload.strip()) is not None


def _git_write_issues(payload: str) -> list[str]:
    if EXPLICIT_GIT_WRITE_MARKER in payload:
        return []
    issues: list[str] = []
    if re.search(r"(?im)^\s*git\s+commit\b", payload):
        issues.append("git_commit_without_explicit_authorization")
    if re.search(r"(?im)^\s*git\s+push\b", payload):
        issues.append("git_push_without_explicit_authorization")
    return issues


def validate_patchops_script_payload_text(text: str, *, path: str | Path = "<memory>") -> ShapeValidationResult:
    payload, issues = extract_single_marked_payload(text)
    checks: dict[str, bool] = {
        "single_payload_marker_pair": not issues,
        "script_surrounded_by_invocation_block": False,
        "strict_mode_present": False,
        "no_encoded_command": True,
        "no_hidden_download": True,
        "no_destructive_or_system_commands": True,
        "git_write_requires_explicit_authorization": True,
    }
    metadata: dict[str, Any] = {
        "payload_begin_count": text.count(SCRIPT_PAYLOAD_BEGIN),
        "payload_end_count": text.count(SCRIPT_PAYLOAD_END),
    }
    if payload is not None:
        checks["script_surrounded_by_invocation_block"] = _has_invocation_block(payload)
        checks["strict_mode_present"] = "Set-StrictMode" in payload
        if not checks["script_surrounded_by_invocation_block"]:
            issues.append("script must be surrounded by & { ... }")
        if not checks["strict_mode_present"]:
            issues.append("Set-StrictMode is required")
        for name, pattern in BANNED_SCRIPT_PATTERNS:
            if re.search(pattern, payload):
                if name == "encoded_command":
                    checks["no_encoded_command"] = False
                elif name == "hidden_download":
                    checks["no_hidden_download"] = False
                else:
                    checks["no_destructive_or_system_commands"] = False
                issues.append(f"blocked_pattern:{name}")
        git_issues = _git_write_issues(payload)
        if git_issues:
            checks["git_write_requires_explicit_authorization"] = False
            issues.extend(git_issues)
        metadata["payload_size_chars"] = len(payload)
    result_label = SCRIPT_PASS_LABEL if not issues else INVALID_LABEL
    return ShapeValidationResult(
        result_label=result_label,
        artifact_kind=SCRIPT_KIND,
        path=Path(path),
        issues=tuple(issues),
        checks=checks,
        metadata=metadata,
    )


def validate_patchops_script_payload_file(path: str | Path) -> ShapeValidationResult:
    artifact_path = Path(path).resolve(strict=False)
    return validate_patchops_script_payload_text(read_script_text(artifact_path), path=artifact_path)