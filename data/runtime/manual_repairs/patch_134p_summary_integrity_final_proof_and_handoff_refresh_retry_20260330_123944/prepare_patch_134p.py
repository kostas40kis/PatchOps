from __future__ import annotations

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

project_status_134o = """
<!-- PATCHOPS_PATCH134O_STATUS:START -->
## Patch 134O - exact-current repair manifest authoring fix

### Current state

- Patch 134O carries the exact-current apply report-write hardening payload through a valid self-hosted manifest shape.
- The patch lands the apply-flow report write hardening in live code and adds the current self-hosted docs-shape regression test.
- The summary-integrity stream should now retry the final proof / handoff refresh step instead of widening the repair scope again.

### Remaining posture

- rerun the maintained summary-integrity proof layer,
- export a refreshed handoff bundle from a current green report,
- record conservative stream closure in maintained docs.
<!-- PATCHOPS_PATCH134O_STATUS:END -->
"""

project_status_134p = """
<!-- PATCHOPS_PATCH134P_STATUS:START -->
## Patch 134P - summary-integrity final proof and handoff refresh retry

### Current state

- Patch 134P reruns the maintained summary-integrity proof layer after Patch 134O landed the exact-current apply report-write hardening.
- Patch 134P refreshes the handoff bundle from a current green report.
- The summary-integrity repair stream can now be treated as complete unless later repo evidence shows a new contradiction between required command evidence and final reported status.

### Remaining posture

- return to the broader maintenance / finalization posture,
- prefer narrow validation, proof, and freeze work over redesign.
<!-- PATCHOPS_PATCH134P_STATUS:END -->
"""

patch_ledger_134o = """
<!-- PATCHOPS_PATCH134O_LEDGER:START -->
## Patch 134O — exact-current repair manifest authoring fix

Patch 134O keeps the exact-current apply report-write hardening payload and repairs only the self-hosted manifest authoring shape.

It lands:
- the exact-current apply-flow report write hardening in `patchops/workflows/apply_patch.py`,
- one current regression test for the self-hosted docs patch shape,
- no widening of the summary-integrity stream.

This is still a narrow maintenance repair patch.
<!-- PATCHOPS_PATCH134O_LEDGER:END -->
"""

patch_ledger_134p = """
<!-- PATCHOPS_PATCH134P_LEDGER:START -->
## Patch 134P — summary-integrity final proof and handoff refresh retry

Patch 134P reruns the maintained summary-integrity proof layer after Patch 134O made the apply-side report write hardening live.

It then:
- refreshes the maintained handoff bundle from a green current report,
- records the stream as complete in maintained docs,
- leaves the repo on a clean green frontier for this repair stream.

This is a narrow proof-and-refresh maintenance patch.
It does not redesign reporting, handoff, manifests, or the workflow model.
<!-- PATCHOPS_PATCH134P_LEDGER:END -->
"""

stream_134o = """
## Patch 134O - exact-current repair manifest authoring fix

Patch 134O keeps the exact-current apply report-write hardening payload and repairs only the manifest authoring shape that blocked Patch 134N.

What it means:
- the apply-flow report write hardening is now live in the current repo,
- the stream now returns to the original final proof / handoff refresh goal,
- there is no need to widen the repair stream into a broader reporting redesign.
"""

stream_134p = """
## Patch 134P - final proof and handoff refresh retry

Patch 134P reruns the maintained summary-integrity proof layer after Patch 134O landed the exact-current apply report-write hardening.

It then refreshes the maintained handoff bundle from the current green report and records the closure state in maintained docs.

Acceptance reached:
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134K report-dir proof-layer repair: complete.
- Patch 134O apply-flow report write hardening / manifest authoring fix: complete.
- Patch 134P final proof and handoff refresh retry: complete.
"""

stream_closure = """
## Closure statement

Treat the summary-integrity repair stream as complete unless later repo evidence shows:
- a new contradiction between required command evidence and final reported status,
- or a new report-preference regression in the same apply-flow report-writing area.
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
        ("PATCHOPS_PATCH134O_STATUS:START", project_status_134o),
        ("PATCHOPS_PATCH134P_STATUS:START", project_status_134p),
    ],
)

stage_doc(
    "docs/patch_ledger.md",
    [
        ("PATCHOPS_PATCH134O_LEDGER:START", patch_ledger_134o),
        ("PATCHOPS_PATCH134P_LEDGER:START", patch_ledger_134p),
    ],
)

stage_doc(
    "docs/summary_integrity_repair_stream.md",
    [
        ("## Patch 134O - exact-current repair manifest authoring fix", stream_134o),
        ("## Patch 134P - final proof and handoff refresh retry", stream_134p),
        ("## Closure statement", stream_closure),
    ],
)

manifest = {
    "manifest_version": "1",
    "patch_name": "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry",
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
                "tests/test_apply_report_write_current.py",
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
        "report_name_prefix": "patch_134p_summary_integrity_final_proof_and_handoff_refresh_retry",
        "write_to_desktop": False,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "final_proof",
        "handoff_refresh",
    ],
    "notes": "Patch 134P reruns the maintained summary-integrity proof layer, refreshes handoff from a current green report, and records stream closure conservatively.",
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(str(manifest_path))