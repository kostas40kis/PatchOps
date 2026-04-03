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

finalization_path = project_root / "docs/finalization_master_plan.md"
test_path = project_root / "tests/test_content_path_finalization_current.py"

finalization_current = finalization_path.read_text(encoding="utf-8")

finalization_block = textwrap.dedent(
    """
    <!-- PATCHOPS_CONTENT_PATH_FINALIZATION:START -->
    ## content_path wrapper-root repair completion note

    This repair stream is complete.

    ### What was closed
    - CP1 proved the duplicated nested patch-prefix bug with a failing current-state repro.
    - CP2 repaired runtime behavior so relative `content_path` values resolve from the wrapper project root first.
    - CP3 aligned docs and examples to the repaired rule.
    - CP4 proved the maintained example manifest end to end.
    - CP5 recorded the stream in the maintained status surfaces.
    - CP6 refreshed the active-work handoff surfaces.
    - CP7 refreshed the new-target onboarding surfaces.

    ### Final maintained rule
    - author relative `content_path` values as wrapper-relative paths from the wrapper project root
    - treat manifest-local resolution as compatibility fallback rather than the primary contract
    - do not reopen this area unless new contrary repo evidence appears

    ### Why this is the closure point
    The repair is now locked across runtime, examples, status, handoff, onboarding, and finalization-facing documentation.
    Any future work here should be narrow maintenance, not redesign.
    <!-- PATCHOPS_CONTENT_PATH_FINALIZATION:END -->
    """
).strip()

if "<!-- PATCHOPS_CONTENT_PATH_FINALIZATION:START -->" not in finalization_current:
    if not finalization_current.endswith("\n"):
        finalization_current += "\n"
    finalization_updated = finalization_current + "\n" + finalization_block + "\n"
else:
    start = "<!-- PATCHOPS_CONTENT_PATH_FINALIZATION:START -->"
    end = "<!-- PATCHOPS_CONTENT_PATH_FINALIZATION:END -->"
    before = finalization_current.split(start, 1)[0]
    after = finalization_current.split(end, 1)[1]
    finalization_updated = before + finalization_block + after

test_content = textwrap.dedent(
    """
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_finalization_plan_mentions_content_path_repair_completion() -> None:
        content = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")
        assert "## content_path wrapper-root repair completion note" in content
        assert "CP1 proved the duplicated nested patch-prefix bug" in content
        assert "CP7 refreshed the new-target onboarding surfaces" in content
        assert "wrapper-relative paths from the wrapper project root" in content
        assert "compatibility fallback rather than the primary contract" in content
        assert "do not reopen this area unless new contrary repo evidence appears" in content
        assert "Any future work here should be narrow maintenance, not redesign." in content
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
            "path": "docs/finalization_master_plan.md",
            "content": finalization_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_path_finalization_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_finalization_closure",
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
    "tags": ["content_path", "finalization", "closure", "contract_lock"],
    "notes": (
        "Eighth repair-stream patch. "
        "This patch records the content_path repair stream as complete in the finalization surface and protects that closure wording with a narrow doc test."
    ),
}

manifest_path = patch_root / "patch_manifest.json"

# IMPORTANT: compact JSON, no trailing newline
manifest_json = json.dumps(manifest, indent=None, separators=(',', ':'))
manifest_path.write_text(manifest_json, encoding="utf-8")

# IMPORTANT: validate immediately before running PatchOps
try:
    with manifest_path.open(encoding="utf-8") as f:
        json.load(f)
except Exception as e:
    raise RuntimeError(
        f"Manifest validation failed: {e}\nContent:\n{manifest_path.read_text(encoding='utf-8')}"
    )

print(json.dumps({
    "manifest_path": str(manifest_path),
    "finalization_path": str(finalization_path),
    "test_path": str(test_path),
}))