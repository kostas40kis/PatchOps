from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PATCH_NAME = "mp21a_baseline_contract_repair"
DEFAULT_LATEST_PATCH = "p134z_final_proof_handoff_refresh"
DEFAULT_NEXT_ACTION = "Retry MP21 single-file writer helper only after the baseline stays green."


def ensure_trailing_newline(value: str) -> str:
    return value if value.endswith("\n") else value + "\n"


def patch_apply_manifest_source(source: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    updated = source

    direct_patterns = [
        (
            "load_content(spec, manifest_path=manifest_path)",
            "load_content(spec, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
            "patched direct load_content call",
        ),
        (
            "build_write_plan(spec, destination, manifest_path=manifest_path)",
            "build_write_plan(spec, destination, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
            "patched positional build_write_plan call",
        ),
        (
            "build_write_plan(spec=spec, destination=destination, manifest_path=manifest_path)",
            "build_write_plan(spec=spec, destination=destination, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
            "patched keyword build_write_plan call",
        ),
    ]

    changed = False
    for old, new, note in direct_patterns:
        if old in updated and new not in updated:
            updated = updated.replace(old, new)
            notes.append(note)
            changed = True

    if not changed:
        regex_patterns = [
            (
                r"load_content\(\s*spec\s*,\s*manifest_path\s*=\s*manifest_path\s*\)",
                "load_content(spec, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
                "patched regex load_content call",
            ),
            (
                r"build_write_plan\(\s*spec\s*,\s*destination\s*,\s*manifest_path\s*=\s*manifest_path\s*\)",
                "build_write_plan(spec, destination, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
                "patched regex positional build_write_plan call",
            ),
            (
                r"build_write_plan\(\s*spec\s*=\s*spec\s*,\s*destination\s*=\s*destination\s*,\s*manifest_path\s*=\s*manifest_path\s*\)",
                "build_write_plan(spec=spec, destination=destination, manifest_path=manifest_path, wrapper_project_root=wrapper_root)",
                "patched regex keyword build_write_plan call",
            ),
        ]
        for pattern, replacement, note in regex_patterns:
            candidate, count = re.subn(pattern, replacement, updated)
            if count:
                updated = candidate
                notes.append(note)
                changed = True
                break

    if not changed:
        notes.append("apply workflow already appeared compatible or no known content-loading call was found")

    return ensure_trailing_newline(updated), notes


def build_repo_state(existing_payload: dict, latest_index: dict) -> dict:
    current_status = (
        latest_index.get("current_status")
        or existing_payload.get("latest_status")
        or existing_payload.get("current_status")
        or "pass"
    )
    failure_class = (
        latest_index.get("failure_class")
        or existing_payload.get("failure_class")
        or existing_payload.get("repo_state", {}).get("failure_class")
        or "none"
    )
    latest_run_mode = (
        existing_payload.get("repo_state", {}).get("latest_run_mode")
        or latest_index.get("latest_run_mode")
        or existing_payload.get("resume_mode")
        or existing_payload.get("recommended_mode")
        or "apply"
    )
    return {
        "current_status": current_status,
        "failure_class": failure_class,
        "latest_run_mode": latest_run_mode,
    }


def build_latest_patch(existing_payload: dict) -> dict:
    existing_latest = existing_payload.get("latest_patch")
    if isinstance(existing_latest, dict):
        latest_passed = existing_latest.get("latest_passed_patch") or existing_payload.get("latest_passed_patch") or DEFAULT_LATEST_PATCH
        latest_attempted = existing_latest.get("latest_attempted_patch") or existing_payload.get("latest_attempted_patch") or latest_passed
        return {
            "latest_passed_patch": latest_passed,
            "latest_attempted_patch": latest_attempted,
        }

    latest_passed = existing_payload.get("latest_passed_patch") or DEFAULT_LATEST_PATCH
    latest_attempted = existing_payload.get("latest_attempted_patch") or latest_passed
    return {
        "latest_passed_patch": latest_passed,
        "latest_attempted_patch": latest_attempted,
    }


def build_next_prompt_text(next_action: str) -> str:
    return ensure_trailing_newline(
        "\n".join(
            [
                "You are resuming the PatchOps project from the current maintained repo state.",
                "",
                "Read these files first:",
                "1. handoff/current_handoff.md",
                "2. handoff/current_handoff.json",
                "3. handoff/latest_report_copy.txt",
                "",
                f"Next recommended action: {next_action}",
                "",
                "Rules:",
                "- keep PowerShell thin",
                "- keep reusable logic in Python",
                "- preserve the one-report evidence contract",
                "- do not move target-repo business logic into PatchOps",
                "- do not redesign the architecture unless the handoff explicitly shows a deeper repo-truth problem",
                "",
                "After reading the handoff, briefly restate:",
                "- current state",
                "- latest attempted patch",
                "- failure class",
                "- next recommended action",
                "",
                "Then produce only the next repair patch or next planned patch.",
            ]
        )
    )


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prepare_mp21a.py <project_root> <working_root>")

    project_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_dir = working_root / "inner_reports"
    manifest_path = working_root / "patch_manifest.json"
    audit_path = working_root / "prepare_audit.txt"

    writers_path = project_root / "patchops" / "files" / "writers.py"
    apply_path = project_root / "patchops" / "workflows" / "apply_patch.py"
    reporting_init_path = project_root / "patchops" / "reporting" / "__init__.py"
    metadata_path = project_root / "patchops" / "reporting" / "metadata.py"
    handoff_json_path = project_root / "handoff" / "current_handoff.json"
    next_prompt_path = project_root / "handoff" / "next_prompt.txt"
    latest_index_path = project_root / "handoff" / "latest_report_index.json"

    apply_source = apply_path.read_text(encoding="utf-8")
    updated_apply_source, apply_patch_notes = patch_apply_manifest_source(apply_source)

    latest_index = json.loads(latest_index_path.read_text(encoding="utf-8")) if latest_index_path.exists() else {}
    existing_handoff = json.loads(handoff_json_path.read_text(encoding="utf-8")) if handoff_json_path.exists() else {}

    next_action = (
        existing_handoff.get("next_action")
        or existing_handoff.get("next_recommended_action")
        or DEFAULT_NEXT_ACTION
    )

    updated_handoff = dict(existing_handoff)
    updated_handoff["repo_state"] = build_repo_state(existing_handoff, latest_index)
    updated_handoff["latest_patch"] = build_latest_patch(existing_handoff)
    updated_handoff["next_action"] = next_action
    if "failure_class" not in updated_handoff:
        updated_handoff["failure_class"] = updated_handoff["repo_state"]["failure_class"]
    if "resume_mode" not in updated_handoff:
        updated_handoff["resume_mode"] = updated_handoff["repo_state"]["latest_run_mode"]

    writers_text = ensure_trailing_newline('''from __future__ import annotations

from pathlib import Path

from patchops.files.paths import ensure_directory
from patchops.models import FileWriteSpec, WritePlan, WriteRecord


def _construct_write_plan(destination: Path, content: str, encoding: str) -> WritePlan:
    candidate_kwargs = (
        {"destination": destination, "content": content, "encoding": encoding},
        {"path": destination, "content": content, "encoding": encoding},
    )
    last_error: Exception | None = None
    for kwargs in candidate_kwargs:
        try:
            return WritePlan(**kwargs)
        except TypeError as exc:  # pragma: no cover - compatibility fallback
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError("Could not construct WritePlan.")


def resolve_content_path(
    spec: FileWriteSpec,
    *,
    manifest_path: Path | None = None,
    wrapper_project_root: Path | None = None,
) -> Path:
    if spec.content_path is None:
        raise ValueError(f"No content source defined for {spec.path}")

    content_path = Path(spec.content_path)
    if content_path.is_absolute():
        return content_path

    candidates: list[Path] = []
    if wrapper_project_root is not None:
        candidates.append(Path(wrapper_project_root) / content_path)
    if manifest_path is not None:
        candidates.append(manifest_path.parent / content_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    if candidates:
        return candidates[0]
    return content_path


def load_content(
    spec: FileWriteSpec,
    manifest_path: Path | None = None,
    wrapper_project_root: Path | None = None,
) -> str:
    if spec.content is not None:
        return spec.content
    source_path = resolve_content_path(
        spec,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_project_root,
    )
    return source_path.read_text(encoding=spec.encoding)


def build_write_plan(
    spec: FileWriteSpec,
    destination: Path,
    *,
    manifest_path: Path | None = None,
    wrapper_project_root: Path | None = None,
) -> WritePlan:
    content = load_content(
        spec,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_project_root,
    )
    return _construct_write_plan(destination=destination, content=content, encoding=spec.encoding)


def write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    ensure_directory(destination.parent)
    destination.write_text(content, encoding=encoding)
    return WriteRecord(path=destination, encoding=encoding)


def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
    return write_single_file(destination, content, encoding=encoding)
''')

    metadata_text = ensure_trailing_newline('''from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from patchops.models import WorkflowResult


@dataclass(slots=True)
class ReportHeaderMetadata:
    mode: str
    patch_name: str
    timestamp: datetime | None
    manifest_path: Path | None
    workspace_root: Path | None
    wrapper_project_root: Path | None
    target_project_root: Path | None
    active_profile: str | None
    runtime_path: Path | None
    backup_root: Path | None
    report_path: Path | None
    manifest_version: str | None


def build_report_header_metadata(
    result: WorkflowResult,
    *,
    timestamp: datetime | None = None,
) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        mode=result.mode,
        patch_name=result.manifest.patch_name,
        timestamp=timestamp,
        manifest_path=result.manifest_path,
        workspace_root=result.workspace_root,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        active_profile=result.resolved_profile.name if result.resolved_profile else None,
        runtime_path=result.runtime_path,
        backup_root=result.backup_root,
        report_path=result.report_path,
        manifest_version=result.manifest.manifest_version,
    )


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def render_report_header_lines(metadata: ReportHeaderMetadata) -> tuple[str, ...]:
    lines = [
        f"PATCHOPS {metadata.mode.upper()}",
        f"Patch Name           : {metadata.patch_name}",
    ]
    if metadata.timestamp is not None:
        lines.append(f"Timestamp            : {metadata.timestamp:%Y-%m-%d %H:%M:%S}")
    lines.extend(
        [
            f"Manifest Path        : {_display_path(metadata.manifest_path)}",
            f"Workspace Root       : {_display_path(metadata.workspace_root)}",
            f"Wrapper Project Root : {_display_path(metadata.wrapper_project_root)}",
            f"Target Project Root  : {_display_path(metadata.target_project_root)}",
            f"Active Profile       : {metadata.active_profile or '(none)'}",
            f"Runtime Path         : {_display_path(metadata.runtime_path)}",
            f"Backup Root          : {_display_path(metadata.backup_root)}",
            f"Report Path          : {_display_path(metadata.report_path)}",
            f"Manifest Version     : {metadata.manifest_version or '(none)'}",
        ]
    )
    return tuple(lines)
''')

    reporting_init_text = ensure_trailing_newline('''"""Reporting utilities for PatchOps."""

from patchops.reporting.metadata import (
    ReportHeaderMetadata,
    build_report_header_metadata,
    render_report_header_lines,
)

__all__ = [
    "ReportHeaderMetadata",
    "build_report_header_metadata",
    "render_report_header_lines",
]
''')

    updated_handoff_text = ensure_trailing_newline(json.dumps(updated_handoff, indent=2, sort_keys=True))
    next_prompt_text = build_next_prompt_text(next_action)

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "apply_path": str(apply_path),
        "metadata_path": str(metadata_path),
        "handoff_json_path": str(handoff_json_path),
        "next_prompt_path": str(next_prompt_path),
        "latest_index_path": str(latest_index_path),
        "writers_exists": writers_path.exists(),
        "apply_exists": apply_path.exists(),
        "reporting_init_exists": reporting_init_path.exists(),
        "handoff_json_exists": handoff_json_path.exists(),
        "next_prompt_exists": next_prompt_path.exists(),
        "latest_index_exists": latest_index_path.exists(),
        "load_content_accepts_wrapper_root_before": "wrapper_project_root" in writers_path.read_text(encoding="utf-8"),
        "report_metadata_file_exists_before": metadata_path.exists(),
        "current_handoff_has_repo_state_before": isinstance(existing_handoff.get("repo_state"), dict),
        "next_prompt_mentions_next_recommended_action_before": "next recommended action" in next_prompt_path.read_text(encoding="utf-8").lower() if next_prompt_path.exists() else False,
        "apply_patch_notes": apply_patch_notes,
    }

    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_dir.mkdir(parents=True, exist_ok=True)

    staged_files = {
        content_root / "patchops" / "files" / "writers.py": writers_text,
        content_root / "patchops" / "workflows" / "apply_patch.py": updated_apply_source,
        content_root / "patchops" / "reporting" / "metadata.py": metadata_text,
        content_root / "patchops" / "reporting" / "__init__.py": reporting_init_text,
        content_root / "handoff" / "current_handoff.json": updated_handoff_text,
        content_root / "handoff" / "next_prompt.txt": next_prompt_text,
    }
    for path, content in staged_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "backup_files": [
            "patchops/files/writers.py",
            "patchops/workflows/apply_patch.py",
            "patchops/reporting/metadata.py",
            "patchops/reporting/__init__.py",
            "handoff/current_handoff.json",
            "handoff/next_prompt.txt",
        ],
        "files_to_write": [
            {"path": "patchops/files/writers.py", "content": writers_text, "encoding": "utf-8"},
            {"path": "patchops/workflows/apply_patch.py", "content": updated_apply_source, "encoding": "utf-8"},
            {"path": "patchops/reporting/metadata.py", "content": metadata_text, "encoding": "utf-8"},
            {"path": "patchops/reporting/__init__.py", "content": reporting_init_text, "encoding": "utf-8"},
            {"path": "handoff/current_handoff.json", "content": updated_handoff_text, "encoding": "utf-8"},
            {"path": "handoff/next_prompt.txt", "content": next_prompt_text, "encoding": "utf-8"},
        ],
        "validation_commands": [
            {
                "name": "full-pytest-quiet",
                "program": "py",
                "args": ["-m", "pytest", "-q"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_dir),
            "report_name_prefix": "mp21a",
            "write_to_desktop": False,
        },
        "tags": [
            "pythonization",
            "baseline_repair",
            "mp21a",
            "self_hosted",
        ],
        "notes": "Repair the red baseline contracts before retrying MP21 single-file writer helper.",
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    audit["manifest_path"] = str(manifest_path)
    audit["staged_files"] = [str(path) for path in staged_files]
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())