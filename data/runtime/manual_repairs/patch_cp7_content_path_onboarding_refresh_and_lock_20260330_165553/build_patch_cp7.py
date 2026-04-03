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

onboarding_md_path = project_root / "onboarding/current_target_bootstrap.md"
onboarding_json_path = project_root / "onboarding/current_target_bootstrap.json"
onboarding_prompt_path = project_root / "onboarding/next_prompt.txt"
test_path = project_root / "tests/test_content_path_onboarding_current.py"

onboarding_md_current = onboarding_md_path.read_text(encoding="utf-8") if onboarding_md_path.exists() else ""
onboarding_json_current = json.loads(onboarding_json_path.read_text(encoding="utf-8")) if onboarding_json_path.exists() else {}
onboarding_prompt_current = onboarding_prompt_path.read_text(encoding="utf-8") if onboarding_prompt_path.exists() else ""

onboarding_md_block = textwrap.dedent(
    """
    <!-- PATCHOPS_CONTENT_PATH_ONBOARDING:START -->
    ## content_path onboarding note

    ### Maintained authoring rule
    - author relative `content_path` values as wrapper-relative paths from the wrapper project root
    - treat manifest-local resolution as compatibility fallback, not the primary contract
    - prefer the maintained example manifest when introducing external content payloads for a new target

    ### Why new-target onboarding should care
    - this avoids reintroducing the duplicated nested patch-prefix bug during first-time target authoring
    - it keeps onboarding guidance aligned with the current runtime behavior, docs, handoff, and tests
    - it keeps future LLMs from treating old manifest-local behavior as the preferred authoring rule
    <!-- PATCHOPS_CONTENT_PATH_ONBOARDING:END -->
    """
).strip()

onboarding_prompt_block = textwrap.dedent(
    """
    [content_path onboarding note]
    - Author relative content_path values as wrapper-relative paths from the wrapper project root.
    - Manifest-local resolution remains compatibility fallback rather than the primary contract.
    - Prefer the maintained generic content-path example when creating a new external-content manifest.
    """
).strip()

if "<!-- PATCHOPS_CONTENT_PATH_ONBOARDING:START -->" not in onboarding_md_current:
    if onboarding_md_current and not onboarding_md_current.endswith("\\n"):
        onboarding_md_current += "\\n"
    onboarding_md_updated = onboarding_md_current + ("\\n" if onboarding_md_current else "") + onboarding_md_block + "\\n"
else:
    start = "<!-- PATCHOPS_CONTENT_PATH_ONBOARDING:START -->"
    end = "<!-- PATCHOPS_CONTENT_PATH_ONBOARDING:END -->"
    before = onboarding_md_current.split(start, 1)[0]
    after = onboarding_md_current.split(end, 1)[1]
    onboarding_md_updated = before + onboarding_md_block + after

onboarding_json_current["content_path_onboarding_rule"] = {
    "authoring_rule": "wrapper_relative_from_wrapper_project_root",
    "fallback_rule": "manifest_local_compatibility_fallback",
    "preferred_example_manifest": "examples/generic_content_path_patch.json",
    "status": "maintenance_locked",
}

if "[content_path onboarding note]" not in onboarding_prompt_current:
    if onboarding_prompt_current and not onboarding_prompt_current.endswith("\\n"):
        onboarding_prompt_current += "\\n"
    onboarding_prompt_updated = onboarding_prompt_current + ("\\n" if onboarding_prompt_current else "") + onboarding_prompt_block + "\\n"
else:
    marker = "[content_path onboarding note]"
    before = onboarding_prompt_current.split(marker, 1)[0]
    onboarding_prompt_updated = before + onboarding_prompt_block + "\\n"

test_content = textwrap.dedent(
    """
    from __future__ import annotations

    import json
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_current_target_bootstrap_mentions_content_path_onboarding_rule() -> None:
        content = (PROJECT_ROOT / "onboarding" / "current_target_bootstrap.md").read_text(encoding="utf-8")
        assert "## content_path onboarding note" in content
        assert "wrapper-relative paths from the wrapper project root" in content
        assert "compatibility fallback" in content
        assert "duplicated nested patch-prefix bug" in content


    def test_current_target_bootstrap_json_mentions_content_path_onboarding_rule() -> None:
        payload = json.loads((PROJECT_ROOT / "onboarding" / "current_target_bootstrap.json").read_text(encoding="utf-8"))
        stream = payload["content_path_onboarding_rule"]
        assert stream["authoring_rule"] == "wrapper_relative_from_wrapper_project_root"
        assert stream["fallback_rule"] == "manifest_local_compatibility_fallback"
        assert stream["preferred_example_manifest"] == "examples/generic_content_path_patch.json"
        assert stream["status"] == "maintenance_locked"


    def test_onboarding_next_prompt_mentions_content_path_onboarding_rule() -> None:
        content = (PROJECT_ROOT / "onboarding" / "next_prompt.txt").read_text(encoding="utf-8")
        assert "[content_path onboarding note]" in content
        assert "wrapper-relative paths from the wrapper project root" in content
        assert "compatibility fallback rather than the primary contract" in content
        assert "generic content-path example" in content
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
            "path": "onboarding/current_target_bootstrap.md",
            "content": onboarding_md_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "onboarding/current_target_bootstrap.json",
            "content": json.dumps(onboarding_json_current, indent=2),
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "onboarding/next_prompt.txt",
            "content": onboarding_prompt_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_path_onboarding_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_onboarding_refresh",
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
    "tags": ["content_path", "onboarding", "docs_stop", "contract_lock"],
    "notes": (
        "Seventh repair-stream patch. "
        "This patch refreshes the onboarding bootstrap surfaces so new-target startup does not reintroduce the repaired content_path bug."
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
        f"Manifest validation failed: {e}\\nContent:\\n{manifest_path.read_text(encoding='utf-8')}"
    )

print(json.dumps({
    "manifest_path": str(manifest_path),
    "onboarding_md_path": str(onboarding_md_path),
    "onboarding_json_path": str(onboarding_json_path),
    "onboarding_prompt_path": str(onboarding_prompt_path),
    "test_path": str(test_path),
}))