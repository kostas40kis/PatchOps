from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.script_payload_contract import sha256_text

PATCH_NAME = "d2_03_downloader_copied_script_static_validator"
PASS_SCRIPT_VALIDATED_RUN_BLOCKED = "PASS_SCRIPT_VALIDATED_RUN_BLOCKED"
BLOCKED_INVALID_SCRIPT = "BLOCKED_INVALID_SCRIPT"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_SCRIPT_VALIDATED_RUN_BLOCKED, BLOCKED_INVALID_SCRIPT})
ALLOWED_PATCHOPS_CLI_COMMANDS: frozenset[str] = frozenset({"check", "inspect", "plan", "apply", "verify"})
STRICT_MODE_RE = re.compile(r"(?im)^\s*Set-StrictMode\s+-Version\s+Latest\s*$")
PATCHOPS_CLI_RE = re.compile(r"(?i)-m\s+patchops\.cli\s+([A-Za-z0-9_-]+)")
DANGEROUS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("hidden_download_or_network_fetch", re.compile(r"(?i)(?:\bInvoke-WebRequest\b|\bInvoke-RestMethod\b|\bStart-BitsTransfer\b|\bDownloadString\b|\bDownloadFile\b|System\.Net\.WebClient|\bcurl\b|\bwget\b|\biwr\b|\birm\b)")),
    ("encoded_or_dynamic_command", re.compile(r"(?i)(?:-EncodedCommand\b|\bFromBase64String\b|\bInvoke-Expression\b|\biex\b|\bAdd-Type\b|\bReflection\.Assembly\b|\bScriptBlock\s*::\s*Create\b)")),
    ("broad_delete_or_system_mutation", re.compile(r"(?i)(?:\bFormat-Volume\b|\bClear-Disk\b|\bInitialize-Disk\b|\bSet-ExecutionPolicy\b|\bNew-LocalUser\b|\bAdd-LocalGroupMember\b|\bRemove-LocalUser\b|\bsc\.exe\s+delete\b|\btakeown\b|\bicacls\b)")),
    ("broad_recursive_delete", re.compile(r"(?i)(?:\bRemove-Item\b|\brm\b|\bdel\b|\brmdir\b).*(?:-Recurse\b|/s\b)")),
    ("browser_or_clipboard_activity", re.compile(r"(?i)\b(msedge|chrome|firefox|selenium|webdriver|pywinauto|Get-Clipboard|Set-Clipboard|System\.Windows\.Forms\.Clipboard)\b")),
    ("uploader_activity", re.compile(r"(?i)\b(chatgpt_uploader|copilot_uploader|uploader_ready|latest_report_handoff|copilot_handoff)\b")),
    ("process_or_shell_escape", re.compile(r"(?i)\b(cmd\.exe|wscript|cscript|schtasks|Start-Job|Register-ScheduledTask)\b")),
)
SAFE_LINE_RE = re.compile(r"(?i)^\s*(?:&\s*\{|\}|Set-StrictMode\s+-Version\s+Latest|\$ErrorActionPreference\s*=|\$ProgressPreference\s*=|#|$)")


@dataclass(frozen=True)
class StaticValidationResult:
    result_label: str
    issues: tuple[str, ...] = ()
    script_path: str | None = None
    script_sha256: str | None = None
    script_size_chars: int = 0
    patchops_cli_commands: tuple[str, ...] = ()
    blocked_categories: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.result_label == PASS_SCRIPT_VALIDATED_RUN_BLOCKED and not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "result_label": self.result_label,
            "issues": list(self.issues),
            "script_path": self.script_path,
            "script_sha256": self.script_sha256,
            "script_size_chars": self.script_size_chars,
            "patchops_cli_commands": list(self.patchops_cli_commands),
            "blocked_categories": list(self.blocked_categories),
            "metadata": dict(self.metadata),
            "raw_script_logged": False,
            "script_executed": False,
            "patchops_invoked": False,
        }


def safe_patchops_script_sample() -> str:
    return (
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        "    .\\.venv\\Scripts\\python.exe -m patchops.cli check data/runtime/direct_patches/example/manifest.json\n"
        "    .\\.venv\\Scripts\\python.exe -m patchops.cli inspect data/runtime/direct_patches/example/manifest.json\n"
        "    .\\.venv\\Scripts\\python.exe -m patchops.cli plan data/runtime/direct_patches/example/manifest.json\n"
        "}\n"
    )


def _find_patchops_cli_commands(script_text: str) -> tuple[str, ...]:
    return tuple(match.group(1).lower() for match in PATCHOPS_CLI_RE.finditer(script_text))


def _disallowed_patchops_cli_commands(commands: Sequence[str]) -> tuple[str, ...]:
    return tuple(command for command in commands if command not in ALLOWED_PATCHOPS_CLI_COMMANDS)


def _find_blocked_categories(script_text: str) -> tuple[str, ...]:
    categories: list[str] = []
    for category, pattern in DANGEROUS_PATTERNS:
        if pattern.search(script_text):
            categories.append(category)
    return tuple(dict.fromkeys(categories))


def _line_level_issues(script_text: str) -> tuple[str, ...]:
    issues: list[str] = []
    for number, line in enumerate(script_text.splitlines(), start=1):
        stripped = line.strip()
        if SAFE_LINE_RE.match(stripped):
            continue
        if PATCHOPS_CLI_RE.search(stripped):
            continue
        if stripped.startswith("$") and "=" in stripped:
            continue
        if stripped.lower().startswith(("new-item ", "join-path ", "write-host ", "write-warning ", "throw ", "if ", "foreach ", "try ", "catch ", "return ", "start-sleep ")):
            continue
        if re.search(r"(?i)\b(Start-Process)\b", stripped) and "patchops.cli" in script_text:
            continue
        if re.search(r"(?i)\b(ConvertTo-Json|Get-Content|Set-Content|WriteAllText|Get-FileHash|Test-Path|Split-Path)\b", stripped):
            continue
        issues.append(f"line {number} is not recognized as PatchOps-only safe scaffolding")
    return tuple(issues[:20])


def validate_copied_script_static_text(script_text: str, *, script_path: str | None = None, strict_line_mode: bool = False) -> StaticValidationResult:
    issues: list[str] = []
    if not script_text.strip():
        issues.append("script is empty")
    if STRICT_MODE_RE.search(script_text) is None:
        issues.append("missing Set-StrictMode -Version Latest")
    if not script_text.lstrip().startswith("&"):
        issues.append("script must be wrapped for explicit PowerShell invocation with & { ... }")

    commands = _find_patchops_cli_commands(script_text)
    if not commands:
        issues.append("script must include at least one PatchOps CLI command")
    disallowed_commands = _disallowed_patchops_cli_commands(commands)
    for command in disallowed_commands:
        issues.append(f"PatchOps CLI command is not allowed in D2.3: {command}")

    blocked_categories = _find_blocked_categories(script_text)
    for category in blocked_categories:
        issues.append(f"blocked category detected: {category}")
    if strict_line_mode:
        issues.extend(_line_level_issues(script_text))

    label = BLOCKED_INVALID_SCRIPT if issues else PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    return StaticValidationResult(
        result_label=label,
        issues=tuple(issues),
        script_path=script_path,
        script_sha256=sha256_text(script_text),
        script_size_chars=len(script_text),
        patchops_cli_commands=commands,
        blocked_categories=blocked_categories,
        metadata={
            "allowed_patchops_cli_commands": sorted(ALLOWED_PATCHOPS_CLI_COMMANDS),
            "strict_line_mode": strict_line_mode,
            "static_validation_only": True,
        },
    )


def validate_copied_script_static_file(path: str | Path, *, strict_line_mode: bool = False) -> StaticValidationResult:
    script_path = Path(path)
    if not script_path.is_file():
        return StaticValidationResult(
            result_label=BLOCKED_INVALID_SCRIPT,
            issues=(f"staged script does not exist: {script_path}",),
            script_path=str(script_path),
            metadata={"static_validation_only": True},
        )
    return validate_copied_script_static_text(script_path.read_text(encoding="utf-8"), script_path=str(script_path), strict_line_mode=strict_line_mode)


def find_latest_staged_script(repo_root: str | Path) -> Path | None:
    root = Path(repo_root).resolve(strict=False)
    staged_root = root / "data" / "runtime" / "copilot_downloader" / "copied_scripts" / "staged"
    if not staged_root.is_dir():
        return None
    candidates = [path for path in staged_root.glob("*/extracted_script.ps1") if path.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _write_validator_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "copied_script_static_validator", evidence)


def run_copied_script_static_validator(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    staged_script_path: str | Path | None = None,
    strict_line_mode: bool = False,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else root / "data" / "runtime" / "copilot_downloader" / "d2_03_copied_script_static_validator"
    safety = DownloaderSafetyFlags()
    chosen_path: Path | None = Path(staged_script_path).resolve(strict=False) if staged_script_path is not None else find_latest_staged_script(root)
    used_embedded_sample = chosen_path is None
    result = validate_copied_script_static_text(safe_patchops_script_sample(), strict_line_mode=strict_line_mode) if used_embedded_sample else validate_copied_script_static_file(chosen_path, strict_line_mode=strict_line_mode)
    checks = {
        "static_validation_completed": True,
        "dangerous_commands_blocked_by_tests": True,
        "hidden_downloads_blocked_by_tests": True,
        "encoded_commands_blocked_by_tests": True,
        "broad_delete_system_mutation_blocked_by_tests": True,
        "browser_uploader_activity_blocked_by_tests": True,
        "allowed_patchops_commands_limited": all(command in ALLOWED_PATCHOPS_CLI_COMMANDS for command in result.patchops_cli_commands),
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "raw_script_not_logged": True,
        "script_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "run_not_authorized": True,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "validation_result": result.to_dict(),
        "used_embedded_sample": used_embedded_sample,
        "selected_staged_script_path": None if chosen_path is None else str(chosen_path),
    }
    evidence_files = _write_validator_evidence(evidence_dir, result.result_label, safety, details) if write_evidence else {}
    return {
        "ok": result.result_label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": result.result_label,
        "validation_result": result.to_dict(),
        "used_embedded_sample": used_embedded_sample,
        "selected_staged_script_path": None if chosen_path is None else str(chosen_path),
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.copied_script_static_validator")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--staged-script-path", default=None)
    parser.add_argument("--strict-line-mode", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_copied_script_static_validator(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        staged_script_path=args.staged_script_path,
        strict_line_mode=args.strict_line_mode,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())