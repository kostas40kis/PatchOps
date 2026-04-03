from __future__ import annotations

import json
from pathlib import Path

PATCH_NAME = "patch_134f_summary_integrity_docs_refresh"

README_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity maintenance repair

The summary-integrity repair stream established and now documents three distinct facts:

- Patch 133 was a wrapper / patch-authoring failure caused by a duplicated `content_path` resolution.
- Patch 133A was the confirmed product-bug repro: required command evidence showed failure while the rendered inner summary still showed `ExitCode : 0` and `Result   : PASS`.
- Patch 134 was a patch-authoring failure caused by malformed JSON, not evidence that the underlying engine repair was wrong.

The repair sequence through Patches 134C-134E keeps the architecture narrow:

- derive rendered summary truth from required command evidence,
- keep explicitly tolerated non-zero exits allowed through `allowed_exit_codes`,
- harden workflow-facing surfaces so CLI and handoff fail closed when stale success state contradicts required command evidence,
- treat the stream as a maintenance repair rather than a redesign.

When sources disagree during this stream, trust current repo files and current tests over historical chat reconstruction.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""

LLM_USAGE_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity repair note for future continuation

The maintained repo story for the summary-integrity stream is now:

- Patch 133 = wrapper / patch-authoring failure (`content_path` duplication)
- Patch 133A = confirmed product bug repro
- Patch 134 = malformed-manifest patch-authoring failure
- Patch 134B = self-hosted authoring unblocker
- Patch 134C = rendered-summary derivation repair
- Patch 134D / 134E = workflow-facing hardening and repair so CLI and handoff agree with effective required-command evidence

For this stream, do not redesign PatchOps.
Use the smallest correct repair class, keep PowerShell thin, keep reusable logic in Python, and treat current repo files plus current tests as the source of truth.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""

OPERATOR_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity operator note

If a future maintenance stream touches report truth again, classify the failure before widening the response:

- wrapper / patch-authoring failure when the patch does not reach validation cleanly,
- product summary-integrity failure when required command evidence contradicts rendered summary state,
- workflow hardening failure when CLI or handoff surfaces disagree with the effective required-command result.

For this class of issue, prefer a narrow self-hosted patch sequence and require one canonical report for each step.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""

PROJECT_STATUS_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity repair stream status

The summary-integrity stream is now in late maintenance / proof posture.

Current maintained interpretation:
- Patch 133 was a wrapper / patch-authoring failure caused by duplicated `content_path` resolution.
- Patch 133A confirmed the real product bug by proving that required command evidence could still coexist with a rendered `PASS` summary.
- Patch 134 was a malformed-manifest authoring failure and did not invalidate the confirmed product bug.
- Patch 134B repaired the self-hosted authoring unblocker for this stream.
- Patch 134C repaired rendered summary derivation for required validation / smoke failures while preserving explicitly tolerated non-zero exits.
- Patch 134D / 134E hardened workflow-facing surfaces so CLI and handoff now fail closed when stale success state conflicts with required command evidence.

The next steps after this doc refresh are proof / freeze work, not architecture redesign.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""

LEDGER_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Patch 134F - summary-integrity docs refresh

Purpose:
- refresh maintained reading surfaces so the repo tells one consistent story about the summary-integrity repair stream.

Delivered:
- refreshed `README.md`, `docs/llm_usage.md`, and `docs/operator_quickstart.md` with the maintained summary-integrity repair narrative,
- refreshed `docs/project_status.md` with the current stream posture,
- refreshed `docs/summary_integrity_repair_stream.md` with the docs-refresh step.

Interpretation:
- this is a narrow documentation refresh after the product fix and workflow hardening,
- it does not redesign PatchOps,
- it prepares the stream for final proof / freeze work.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""

STREAM_BLOCK = """<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Patch 134F - maintained doc refresh

Patch 134F refreshes the maintained reading surfaces so future LLMs and operators can understand the stream from repo files alone.

It records the now-maintained interpretation:
- Patch 133 = wrapper / patch-authoring failure,
- Patch 133A = confirmed product bug repro,
- Patch 134 = malformed-manifest authoring failure,
- Patch 134B = authoring unblocker,
- Patch 134C = rendered-summary derivation repair,
- Patch 134D / 134E = workflow-facing fail-closed hardening.

This patch intentionally keeps the story narrow and maintenance-oriented.
The remaining stream work is proof / freeze validation rather than redesign.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->
"""


def append_block(text: str, block: str) -> str:
    start = block.splitlines()[0].strip()
    end = block.splitlines()[-1].strip()
    if start in text and end in text:
        return text
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    return text + block


def write_content_file(content_root: Path, relative_path: str, text: str) -> None:
    out_path = content_root / relative_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_root = Path(__file__).resolve().parent
    project_root = patch_root.parents[3]
    content_root = patch_root / "content"
    content_root.mkdir(parents=True, exist_ok=True)

    updates = {
        "README.md": README_BLOCK,
        "docs/llm_usage.md": LLM_USAGE_BLOCK,
        "docs/operator_quickstart.md": OPERATOR_BLOCK,
        "docs/project_status.md": PROJECT_STATUS_BLOCK,
        "docs/patch_ledger.md": LEDGER_BLOCK,
        "docs/summary_integrity_repair_stream.md": STREAM_BLOCK,
    }

    for relative_path, block in updates.items():
        source_text = (project_root / relative_path).read_text(encoding="utf-8")
        updated_text = append_block(source_text, block)
        write_content_file(content_root, relative_path, updated_text)

    validate_code = """from __future__ import annotations
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
checks = {
    root / 'README.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'llm_usage.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'operator_quickstart.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'project_status.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'patch_ledger.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
    root / 'docs' / 'summary_integrity_repair_stream.md': 'PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START',
}
for path, needle in checks.items():
    text = path.read_text(encoding='utf-8')
    if needle not in text:
        raise SystemExit(f'missing marker in {path}')
print('patch_134f validation passed')
"""
    (patch_root / "validate_patch_134f.py").write_text(validate_code, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {"path": path.replace("/", "\\"), "content_path": (Path("content") / Path(path)).as_posix().replace("/", "\\"), "encoding": "utf-8"}
            for path in updates.keys()
        ],
        "validation_commands": [
            {
                "name": "patch_134f_docs_refresh_validation",
                "program": "py",
                "args": ["validate_patch_134f.py", str(project_root)],
                "working_directory": str(patch_root),
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(patch_root / "inner_reports"),
            "report_name_prefix": PATCH_NAME,
            "write_to_desktop": True,
        },
        "tags": ["summary_integrity", "self_hosted", "docs_refresh"],
        "notes": "Patch 134F refreshes maintained reading surfaces so the summary-integrity repair stream is understandable from current repo docs without chat history.",
    }

    manifest_path = patch_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(str(manifest_path))


if __name__ == "__main__":
    main()