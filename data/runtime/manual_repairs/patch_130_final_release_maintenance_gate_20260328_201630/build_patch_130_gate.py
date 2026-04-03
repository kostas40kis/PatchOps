from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

wrapper_root = Path(sys.argv[1]).resolve()
stage_root = Path(sys.argv[2]).resolve()
manifest_path = Path(sys.argv[3]).resolve()
patch_name = "patch_130_final_release_maintenance_gate"
latest_report = r"C:\Users\kostas\Desktop\patch_129k_new_target_onboarding_current_contract_repair_20260328_195939.txt"
python_exe = sys.executable

def read_text_or_default(path: Path, default: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default

def append_unique_block(existing: str, block: str, marker: str) -> str:
    if marker in existing:
        return existing
    base = existing.rstrip()
    if base:
        return base + "\n\n" + block.strip() + "\n"
    return block.strip() + "\n"

def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text, encoding="utf-8")

def rel_to_wrapper(path: Path) -> str:
    return path.relative_to(wrapper_root).as_posix()

project_status_path = wrapper_root / "docs" / "project_status.md"
patch_ledger_path = wrapper_root / "docs" / "patch_ledger.md"
readiness_report_path = stage_root / "release_readiness_f6.txt"

project_status_block = dedent(f"""
<!-- PATCHOPS_F6_GATE_STATUS:START -->
## Patch 130 - final release / maintenance gate

### Verified input state before this gate

- F1 truth-reset completed.
- F2 final self-contained master documentation completed.
- F3 final contract-lock validation sweep completed.
- F4 active-work continuation flow proof completed.
- F5 new-target onboarding flow proof completed.
- latest successful patch before this gate: Patch 129K — `patch_129k_new_target_onboarding_current_contract_repair`
- latest trusted report before this gate: `{latest_report}`

### Gate intent

Patch 130 is the final release / maintenance gate patch.
Its job is to confirm, through the shipped readiness and full-suite validation surfaces, that PatchOps can now be described honestly as:

- complete as an initial product,
- in maintenance mode,
- open only to additive or target-specific future work.

### Boundary reminder

Do not redesign the architecture during this gate.
Use the current readiness, handoff, onboarding, example, and profile surfaces as shipped, and repair only what validation proves is still drifting.
<!-- PATCHOPS_F6_GATE_STATUS:END -->
""").strip()

patch_ledger_block = dedent("""
## Patch 130

Patch 130 adds the final release / maintenance gate surface.

It records the verified pre-gate posture after Patch 129K, appends an explicit F6 gate status block to `docs/project_status.md`, and adds `tests/test_final_release_maintenance_gate.py` so the maintained docs, handoff bundle files, project-packet examples, key profiles, and operator launchers have to exist together before the repo can be described as maintenance-ready.

This patch is intentionally narrow.
It is a gate patch, not a redesign patch.
""").strip()

test_text = dedent("""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_GATE_PATHS = (
    "README.md",
    "docs/project_status.md",
    "docs/llm_usage.md",
    "docs/operator_quickstart.md",
    "docs/examples.md",
    "docs/handoff_surface.md",
    "docs/project_packet_workflow.md",
    "docs/project_packet_contract.md",
    "docs/patch_ledger.md",
    "docs/finalization_master_plan.md",
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "handoff/current_handoff.md",
    "handoff/current_handoff.json",
    "handoff/latest_report_copy.txt",
    "docs/projects/trader.md",
    "docs/projects/wrapper_self_hosted.md",
    "examples/generic_python_patch.json",
    "examples/generic_python_powershell_patch.json",
    "examples/trader_code_patch.json",
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
    "patchops/profiles/trader.py",
    "patchops/profiles/generic_python.py",
    "patchops/profiles/generic_python_powershell.py",
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchReadiness.ps1",
    "powershell/Invoke-PatchHandoff.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
)

def test_f6_required_release_gate_surfaces_exist() -> None:
    missing = [relative for relative in REQUIRED_GATE_PATHS if not (PROJECT_ROOT / relative).exists()]
    assert not missing, "missing final release gate surface(s): " + ", ".join(missing)

def test_f6_project_status_records_current_gate_posture() -> None:
    text = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "patchops_f6_gate_status:start" in lowered
    assert "patch 129k" in lowered
    assert "patch 130" in lowered
    assert "maintenance mode" in lowered
    assert "complete as an initial product" in lowered
    assert "additive or target-specific future work" in lowered

def test_f6_patch_ledger_records_gate_patch() -> None:
    text = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "## Patch 130" in text
    assert "final release / maintenance gate surface" in lowered
    assert "gate patch, not a redesign patch" in lowered
""").strip() + "\n"

current_project_status = read_text_or_default(project_status_path, "# PatchOps project status\n")
current_patch_ledger = read_text_or_default(patch_ledger_path, "# PatchOps patch ledger\n")

next_project_status = append_unique_block(
    current_project_status,
    project_status_block,
    "PATCHOPS_F6_GATE_STATUS:START",
)
next_patch_ledger = append_unique_block(
    current_patch_ledger,
    patch_ledger_block,
    "## Patch 130",
)

staged_project_status = stage_root / "docs" / "project_status.md"
staged_patch_ledger = stage_root / "docs" / "patch_ledger.md"
staged_test = stage_root / "tests" / "test_final_release_maintenance_gate.py"

write_text(staged_project_status, next_project_status)
write_text(staged_patch_ledger, next_patch_ledger)
write_text(staged_test, test_text)

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python_powershell",
    "target_project_root": str(wrapper_root).replace("\\", "/"),
    "backup_files": [
        "docs/project_status.md",
        "docs/patch_ledger.md",
        "tests/test_final_release_maintenance_gate.py",
    ],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content": None,
            "content_path": rel_to_wrapper(staged_project_status),
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content": None,
            "content_path": rel_to_wrapper(staged_patch_ledger),
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_final_release_maintenance_gate.py",
            "content": None,
            "content_path": rel_to_wrapper(staged_test),
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "full_pytest",
            "program": python_exe,
            "args": ["-m", "pytest", "-q"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
        {
            "name": "release_readiness",
            "program": python_exe,
            "args": [
                "-m",
                "patchops.cli",
                "release-readiness",
                "--wrapper-root",
                ".",
                "--profile",
                "generic_python_powershell",
                "--core-tests-green",
                "--report-path",
                str(readiness_report_path),
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
    ],
    "smoke_commands": [],
    "audit_commands": [
        {
            "name": "profiles_summary",
            "program": python_exe,
            "args": ["-m", "patchops.cli", "profiles", "--wrapper-root", "."],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
        {
            "name": "examples_index",
            "program": python_exe,
            "args": ["-m", "patchops.cli", "examples"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
    ],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": None,
        "report_name_prefix": patch_name,
        "write_to_desktop": True,
    },
    "tags": [
        "finalization",
        "f6",
        "maintenance_gate",
        "self_hosted",
    ],
    "notes": "F6 final release / maintenance gate patch for PatchOps self-hosted finalization.",
}

ensure_parent(manifest_path)
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(str(manifest_path))