import sys
from pathlib import Path

project_root = Path(r"C:\dev\patchops")
target_path = project_root / "patchops" / "workflows" / "verify_only.py"

text = target_path.read_text(encoding="utf-8")
if "def resolve_verify_only_expected_target_files(" in text:
    print("Skipped: patch already applied.")
    sys.exit(0)

helper_block = """

# PATCHOPS_MP08A_VERIFY_ONLY_HELPERS_RESTORE_START
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class VerifyOnlyFlowState:
    mode: str
    writes_skipped: bool
    expected_target_files: tuple[str, ...]
    existing_target_files: tuple[str, ...]
    missing_target_files: tuple[str, ...]
    validation_command_count: int
    smoke_command_count: int
    audit_command_count: int


def _verify_only_iter_manifest_paths(manifest: Mapping[str, Any]) -> list[str]:
    values: list[str] = []

    explicit_targets = manifest.get("target_files") or []
    for value in explicit_targets:
        if isinstance(value, str) and value.strip():
            values.append(value.strip())

    files_to_write = manifest.get("files_to_write") or []
    for item in files_to_write:
        if isinstance(item, Mapping):
            path_value = item.get("path")
            if isinstance(path_value, str) and path_value.strip():
                values.append(path_value.strip())

    return values


def resolve_verify_only_expected_target_files(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
) -> list[str]:
    target_root = Path(str(target_project_root))
    resolved: list[str] = []
    seen: set[str] = set()

    for raw in _verify_only_iter_manifest_paths(manifest):
        path = Path(raw)
        candidate = path if path.is_absolute() else target_root / path
        normalized = str(candidate)
        if normalized not in seen:
            seen.add(normalized)
            resolved.append(normalized)

    return resolved


def build_verify_only_flow_state(
    manifest: Mapping[str, Any],
    target_project_root: str | Path,
) -> VerifyOnlyFlowState:
    expected = tuple(resolve_verify_only_expected_target_files(manifest, target_project_root))
    existing = tuple(path for path in expected if Path(path).exists())
    missing = tuple(path for path in expected if not Path(path).exists())

    validation_commands = manifest.get("validation_commands") or []
    smoke_commands = manifest.get("smoke_commands") or []
    audit_commands = manifest.get("audit_commands") or []

    return VerifyOnlyFlowState(
        mode="verify",
        writes_skipped=True,
        expected_target_files=expected,
        existing_target_files=existing,
        missing_target_files=missing,
        validation_command_count=len(validation_commands),
        smoke_command_count=len(smoke_commands),
        audit_command_count=len(audit_commands),
    )


def render_verify_only_scope_lines(state: VerifyOnlyFlowState) -> tuple[str, ...]:
    return (
        "Scope    : verification-only rerun",
        f"Mode     : {state.mode}",
        "Writes   : skipped",
        "Intent   : re-check files already on disk and rerun validation commands",
        f"Expected : {len(state.expected_target_files)}",
        f"Existing : {len(state.existing_target_files)}",
        f"Missing  : {len(state.missing_target_files)}",
        f"Validate : {state.validation_command_count}",
        f"Smoke    : {state.smoke_command_count}",
        f"Audit    : {state.audit_command_count}",
    )


def verify_only_flow_needs_attention(state: VerifyOnlyFlowState) -> bool:
    return bool(state.missing_target_files)
# PATCHOPS_MP08A_VERIFY_ONLY_HELPERS_RESTORE_END
"""

if not text.endswith("\n"):
    text += "\n"
text += helper_block + "\n"
target_path.write_text(text, encoding="utf-8")
print("Applied patch.")