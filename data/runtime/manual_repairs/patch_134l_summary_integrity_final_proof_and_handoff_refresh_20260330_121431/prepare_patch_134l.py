import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()

content_root = patch_root / "content"
(content_root / "docs").mkdir(parents=True, exist_ok=True)
(patch_root / "inner_reports").mkdir(parents=True, exist_ok=True)

def append_block_if_missing(text: str, marker: str, block: str) -> str:
    if marker in text:
        return text
    return text.rstrip() + "\n\n" + block.strip() + "\n"

project_status_134k = """
<!-- PATCHOPS_PATCH134K_STATUS:START -->
## Patch 134K - report-dir proof layer repair

### Current state

- Patch 134K repairs the remaining report-dir proof-layer drift left after Patch 134H through Patch 134J.
- The maintained report-preference apply-flow proof is now a valid current test surface again.
- The maintained interpretation remains:
  - Patch 134H fixed the apply-flow report-directory creation bug itself,
  - and the remaining work after Patch 134K is the final proof / handoff refresh step only.

### Remaining posture

- rerun the maintained summary-integrity proof layer,
- refresh the handoff bundle from the current green report,
- record closure conservatively without widening the stream into redesign.
<!-- PATCHOPS_PATCH134K_STATUS:END -->
"""

project_status_134l = """
<!-- PATCHOPS_PATCH134L_STATUS:START -->
## Patch 134L - summary-integrity final proof and handoff refresh

### Current state

- Patch 134L reruns the maintained summary-integrity proof layer after Patch 134K returned the report-dir proof surface to green.
- Patch 134L refreshes the maintained handoff bundle from the current green report.
- The summary-integrity repair stream can now be treated as complete unless later repo evidence shows a new contradiction between required command evidence and final reported status.

### Remaining posture

- return to the broader maintenance / finalization posture,
- prefer narrow validation, proof, and freeze work over redesign.
<!-- PATCHOPS_PATCH134L_STATUS:END -->
"""

patch_ledger_134k = """
<!-- PATCHOPS_PATCH134K_LEDGER:START -->
## Patch 134K — report-dir proof layer repair

Patch 134K closes the remaining report-dir proof-layer drift left after Patch 134H through Patch 134J.

What it does:
- repairs the current report-preference apply-flow proof layer,
- uses structured manifest authoring and explicit runtime selection through `sys.executable`,
- keeps the apply-flow code repair from Patch 134H unchanged.

This is a narrow proof repair patch.
It does not redesign the apply flow or the reporting subsystem.
<!-- PATCHOPS_PATCH134K_LEDGER:END -->
"""

patch_ledger_134l = """
<!-- PATCHOPS_PATCH134L_LEDGER:START -->
## Patch 134L — summary-integrity final proof and handoff refresh

Patch 134L reruns the maintained summary-integrity proof layer after Patch 134K returned the report-dir proof surface to green.

It then:
- refreshes the maintained handoff bundle from a current green report,
- records the stream as complete in maintained docs,
- leaves the repo on a clean green frontier for this repair stream.

This is a narrow proof-and-refresh maintenance patch.
It does not redesign reporting, handoff, manifests, or the workflow model.
<!-- PATCHOPS_PATCH134L_LEDGER:END -->
"""

stream_134k = """
## Patch 134K - report-dir proof layer repair

Patch 134K repairs the remaining proof-layer drift left after Patch 134H through Patch 134J.

What it changes:
- the maintained report-preference apply-flow proof is rewritten as valid current tests,
- the proof now uses structured manifests and `sys.executable` for the validation command,
- the underlying apply-flow code repair from Patch 134H remains unchanged.

Interpretation:
- Patch 134H fixed the missing-report-dir creation bug in live code,
- Patch 134K repaired the proof layer around that fix,
- the remaining work after Patch 134K is the final proof / handoff refresh step only.
"""

stream_134l = """
## Patch 134L - final proof and handoff refresh retry

Patch 134L reruns the maintained summary-integrity proof layer after Patch 134K returned the report-dir proof surface to green.

It then refreshes the maintained handoff bundle from the current green report and records the closure state in maintained docs.

Acceptance reached:
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134H apply-flow report-directory creation repair: complete.
- Patch 134K report-dir proof-layer repair: complete.
- Patch 134L final proof and handoff refresh: complete.
"""

stream_closure = """
## Closure statement

Treat the summary-integrity repair stream as complete unless later repo evidence shows:
- a new contradiction between required command evidence and final reported status,
- or a new report-preference regression in the same apply-flow report-directory area.
"""

def stage_doc(relative_path: str, blocks: list[tuple[str, str]]) -> None:
    repo_path = project_root / relative_path
    text = repo_path.read_text(encoding="utf-8")
    for marker, block in blocks:
        text = append_block_if_missing(text, marker, block)
    output_path = content_root / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")

stage_doc(
    "docs/project_status.md",
    [
        ("PATCHOPS_PATCH134K_STATUS:START", project_status_134k),
        ("PATCHOPS_PATCH134L_STATUS:START", project_status_134l),
    ],
)

stage_doc(
    "docs/patch_ledger.md",
    [
        ("PATCHOPS_PATCH134K_LEDGER:START", patch_ledger_134k),
        ("PATCHOPS_PATCH134L_LEDGER:START", patch_ledger_134l),
    ],
)

stage_doc(
    "docs/summary_integrity_repair_stream.md",
    [
        ("## Patch 134K - report-dir proof layer repair", stream_134k),
        ("## Patch 134L - final proof and handoff refresh retry", stream_134l),
        ("## Closure statement", stream_closure),
    ],
)

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134l_summary_integrity_final_proof_and_handoff_refresh",
    "active_profile": "generic_python",
    "target_project_root": str(project_root).replace("\\", "/"),
    "backup_files": [
        "docs/project_status.md",
        "docs/patch_ledger.md",
        "docs/summary_integrity_repair_stream.md",
        "handoff/current_handoff.md",
        "handoff/current_handoff.json",
        "handoff/latest_report_copy.txt",
        "handoff/latest_report_index.json",
        "handoff/next_prompt.txt",
    ],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content": None,
            "content_path": "content/docs/project_status.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content": None,
            "content_path": "content/docs/patch_ledger.md",
            "encoding": "utf-8",
        },
        {
            "path": "docs/summary_integrity_repair_stream.md",
            "content": None,
            "content_path": "content/docs/summary_integrity_repair_stream.md",
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "summary_integrity_final_proof_pytest",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_summary_integrity_current.py",
                "tests/test_summary_integrity_workflow_current.py",
                "tests/test_report_preference_apply_flow.py",
                "tests/test_report_preference_apply_flow_current.py",
                "tests/test_report_preference_examples.py",
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "smoke_commands": [],
    "audit_commands": [],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": str((patch_root / "inner_reports")).replace("\\", "/"),
        "report_name_prefix": "patch_134l_summary_integrity_final_proof_and_handoff_refresh",
        "write_to_desktop": False,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "final_proof",
        "handoff_refresh",
    ],
    "notes": "Patch 134L reruns the maintained summary-integrity proof layer, refreshes handoff from a green current report, and records stream closure conservatively.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))