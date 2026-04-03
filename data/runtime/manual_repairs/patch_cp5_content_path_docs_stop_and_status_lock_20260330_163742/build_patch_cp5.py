from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()
desktop = Path(sys.argv[3]).resolve()
patch_name = sys.argv[4]
validation_program = sys.argv[5]
validation_args_path = Path(sys.argv[6]).resolve()
validation_args = json.loads(validation_args_path.read_text(encoding="utf-8"))

project_status_path = project_root / "docs/project_status.md"
patch_ledger_path = project_root / "docs/patch_ledger.md"
test_path = project_root / "tests/test_content_path_status_current.py"

project_status_current = project_status_path.read_text(encoding="utf-8")
patch_ledger_current = patch_ledger_path.read_text(encoding="utf-8")

project_status_block = textwrap.dedent(
    """
    <!-- PATCHOPS_CONTENT_PATH_STATUS:START -->
    ## content_path wrapper-root repair stream

    ### Current state

    - The wrapper-relative `content_path` bug is repaired.
    - Relative `content_path` values are now resolved from the wrapper project root first.
    - Manifest-local resolution is still preserved as a compatibility fallback when the wrapper-root candidate does not exist.
    - The maintained example manifest now has an end-to-end apply-flow proof.

    ### Why this matters

    - the maintained authoring contract now matches runtime behavior,
    - nested self-hosted patch directories no longer duplicate the patch-root prefix during `apply`,
    - docs, examples, and tests now describe the same rule,
    - future drift is more likely to trigger a narrow honest repair instead of another ambiguous operator failure.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation or doc-contract patches when the behavior is already shipped and the main risk is wording drift.
    <!-- PATCHOPS_CONTENT_PATH_STATUS:END -->
    """
).strip()

patch_ledger_block = textwrap.dedent(
    """
    <!-- PATCHOPS_CONTENT_PATH_LEDGER:START -->
    ## content_path wrapper-root repair stream

    ### CP1 - current-state repro contract
    - Added a failing current-state repro test for wrapper-relative `content_path`.
    - Proved the duplicated nested patch-prefix failure as a wrapper-side path-resolution bug.

    ### CP2 - wrapper-root resolution repair
    - Repaired relative `content_path` resolution so the wrapper-root candidate is checked first.
    - Preserved manifest-local fallback for older nested-manifest flows.
    - Added direct resolver tests in `tests/test_writers.py`.

    ### CP3 - docs and example alignment
    - Refreshed `docs/manifest_schema.md` and `docs/examples.md` so the maintained authoring rule is explicit.
    - Recorded that manifest-local resolution remains compatibility fallback rather than the primary contract.
    - Refreshed the maintained example payload and example-contract tests.

    ### CP4 - example apply-flow proof
    - Added an end-to-end current-state apply-flow proof for `examples/generic_content_path_patch.json`.
    - Confirmed that the maintained example now applies successfully with wrapper-relative `content_path`.

    ### Current outcome
    - The `content_path` repair stream is green through CP4.
    - The remaining work is documentation stop and normal maintenance rather than runtime redesign.
    <!-- PATCHOPS_CONTENT_PATH_LEDGER:END -->
    """
).strip()

if "<!-- PATCHOPS_CONTENT_PATH_STATUS:START -->" not in project_status_current:
    if not project_status_current.endswith("\n"):
        project_status_current += "\n"
    project_status_updated = project_status_current + "\n" + project_status_block + "\n"
else:
    start = "<!-- PATCHOPS_CONTENT_PATH_STATUS:START -->"
    end = "<!-- PATCHOPS_CONTENT_PATH_STATUS:END -->"
    before = project_status_current.split(start, 1)[0]
    after = project_status_current.split(end, 1)[1]
    project_status_updated = before + project_status_block + after

if "<!-- PATCHOPS_CONTENT_PATH_LEDGER:START -->" not in patch_ledger_current:
    if not patch_ledger_current.endswith("\n"):
        patch_ledger_current += "\n"
    patch_ledger_updated = patch_ledger_current + "\n" + patch_ledger_block + "\n"
else:
    start = "<!-- PATCHOPS_CONTENT_PATH_LEDGER:START -->"
    end = "<!-- PATCHOPS_CONTENT_PATH_LEDGER:END -->"
    before = patch_ledger_current.split(start, 1)[0]
    after = patch_ledger_current.split(end, 1)[1]
    patch_ledger_updated = before + patch_ledger_block + after

test_content = textwrap.dedent(
    """
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_project_status_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
        assert "## content_path wrapper-root repair stream" in content
        assert "wrapper project root first" in content
        assert "compatibility fallback" in content
        assert "example manifest now has an end-to-end apply-flow proof" in content


    def test_patch_ledger_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
        assert "## content_path wrapper-root repair stream" in content
        assert "### CP1 - current-state repro contract" in content
        assert "### CP2 - wrapper-root resolution repair" in content
        assert "### CP3 - docs and example alignment" in content
        assert "### CP4 - example apply-flow proof" in content
        assert "remaining work is documentation stop and normal maintenance" in content
    """
).lstrip()

patch_root.mkdir(parents=True, exist_ok=True)

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python",
    "target_project_root": project_root.as_posix(),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content": project_status_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content": patch_ledger_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_path_status_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_docs_stop",
            "program": validation_program,
            "args": validation_args,
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
        "report_dir": desktop.as_posix(),
        "report_name_prefix": patch_name,
        "write_to_desktop": False,
    },
    "tags": ["content_path", "docs_stop", "patch_ledger", "project_status", "contract_lock"],
    "notes": (
        "Fifth repair-stream patch. "
        "This patch records the content_path repair stream in project_status and patch_ledger "
        "and adds one narrow status-surface contract test."
    ),
}

manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

print(json.dumps({
    "manifest_path": str(manifest_path),
    "project_status_path": str(project_status_path),
    "patch_ledger_path": str(patch_ledger_path),
    "test_path": str(test_path),
}))