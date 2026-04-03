from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PATCH_NAME = "patch_134g_summary_integrity_final_proof_and_handoff_refresh"

PROJECT_STATUS_BLOCK = """<!-- PATCHOPS_PATCH134G_STATUS:START -->
## Patch 134G - summary-integrity proof and handoff refresh

Patch 134G closes the six-patch summary-integrity repair circle with a proof-and-refresh run.

It proves the repaired state by running the maintained summary-integrity validation layer:
- `tests/test_summary_integrity_current.py`
- `tests/test_summary_integrity_workflow_current.py`
- `tests/test_reporting.py`
- `tests/test_failure_classifier.py`
- `tests/test_handoff_failure_modes.py`
- `tests/test_export_handoff_cli_contract.py`

It also refreshes the maintained handoff bundle from a green current report so future continuation can rely on:
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`

Current summary-integrity repair posture:
- Patch 134A recorded the truth reset and separated the confirmed product bug from the authoring failures.
- Patch 134B repaired the narrow self-hosted authoring unblocker.
- Patch 134C repaired rendered summary derivation so required validation/smoke failures can no longer render `PASS`.
- Patch 134E completed the workflow hardening repair so CLI and handoff also fail closed when required command evidence contradicts stale success state.
- Patch 134G now treats this stream as complete unless later evidence proves another contradiction.
<!-- PATCHOPS_PATCH134G_STATUS:END -->"""

LEDGER_BLOCK = """<!-- PATCHOPS_PATCH134G_LEDGER:START -->
## Patch 134G

Patch 134G is the final proof and handoff-refresh patch for the summary-integrity repair stream.

It does three things:
- reruns the maintained summary-integrity proof layer,
- refreshes the maintained handoff bundle from a green current report,
- records the stream as complete unless later evidence proves another contradiction.

This is a narrow proof-and-refresh maintenance patch.
It does not redesign reporting, handoff, manifests, or the workflow model.
<!-- PATCHOPS_PATCH134G_LEDGER:END -->"""

STREAM_BLOCK = """<!-- PATCHOPS_PATCH134G_STREAM:START -->
## Patch 134G - final proof and handoff refresh

Patch 134G is the closing proof patch for the six-patch summary-integrity repair circle.

### What it proves
- the rendered report summary no longer claims `PASS` when required validation or smoke evidence failed outside `allowed_exit_codes`,
- CLI-facing and handoff-facing workflow surfaces also fail closed when required command evidence contradicts stale success state,
- the maintained handoff bundle can be refreshed from a green current report after the repair stream.

### Acceptance reached
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134G proof and handoff refresh: complete.

### Current closure statement
Treat the summary-integrity repair stream as complete unless later repo evidence shows another contradiction between required command evidence and final reported status.
<!-- PATCHOPS_PATCH134G_STREAM:END -->"""

def upsert_marker(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(block, text, count=1)
    text = text.rstrip() + "\n\n" + block + "\n"
    return text

def main() -> int:
    project_root = Path(sys.argv[1]).resolve()
    patch_root = Path(sys.argv[2]).resolve()
    content_root = patch_root / "content"
    docs_content_root = content_root / "docs"
    docs_content_root.mkdir(parents=True, exist_ok=True)

    targets = {
        "docs/project_status.md": PROJECT_STATUS_BLOCK,
        "docs/patch_ledger.md": LEDGER_BLOCK,
        "docs/summary_integrity_repair_stream.md": STREAM_BLOCK,
    }

    for relative_path, block in targets.items():
        source_path = project_root / relative_path
        text = source_path.read_text(encoding="utf-8")
        start = block.splitlines()[0]
        end = block.splitlines()[-1]
        updated = upsert_marker(text, start, end, block)
        destination = content_root / Path(relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(updated, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {
                "path": "docs/project_status.md",
                "content_path": "content/docs/project_status.md",
                "encoding": "utf-8",
            },
            {
                "path": "docs/patch_ledger.md",
                "content_path": "content/docs/patch_ledger.md",
                "encoding": "utf-8",
            },
            {
                "path": "docs/summary_integrity_repair_stream.md",
                "content_path": "content/docs/summary_integrity_repair_stream.md",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "summary_integrity_final_proof",
                "program": "py",
                "args": [
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_summary_integrity_current.py",
                    "tests/test_summary_integrity_workflow_current.py",
                    "tests/test_reporting.py",
                    "tests/test_failure_classifier.py",
                    "tests/test_handoff_failure_modes.py",
                    "tests/test_export_handoff_cli_contract.py",
                ],
                "working_directory": str(project_root),
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(patch_root / "inner_reports"),
            "report_name_prefix": PATCH_NAME,
            "write_to_desktop": True,
        },
        "tags": ["summary_integrity", "self_hosted", "proof_refresh"],
        "notes": "Patch 134G reruns the maintained summary-integrity proof layer and refreshes the handoff bundle from a green current report.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(str(manifest_path))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())