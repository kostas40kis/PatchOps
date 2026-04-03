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

handoff_md_path = project_root / "handoff/current_handoff.md"
handoff_json_path = project_root / "handoff/current_handoff.json"
next_prompt_path = project_root / "handoff/next_prompt.txt"
test_path = project_root / "tests/test_content_path_handoff_current.py"

handoff_md_current = handoff_md_path.read_text(encoding="utf-8") if handoff_md_path.exists() else ""
handoff_json_current = json.loads(handoff_json_path.read_text(encoding="utf-8")) if handoff_json_path.exists() else {}
next_prompt_current = next_prompt_path.read_text(encoding="utf-8") if next_prompt_path.exists() else ""

handoff_md_block = textwrap.dedent(
    """
    <!-- PATCHOPS_CONTENT_PATH_HANDOFF:START -->
    ## content_path repair stream

    ### Current status
    - green through CP5
    - wrapper-relative `content_path` bug repaired
    - relative `content_path` values resolve from the wrapper project root first
    - manifest-local resolution remains compatibility fallback when the wrapper-root candidate does not exist
    - the maintained generic content-path example now has an end-to-end apply-flow proof

    ### Next posture
    - do not reopen content-path runtime redesign unless new contrary evidence appears
    - treat this area as maintenance-locked and covered by current tests
    - prefer narrow follow-up maintenance only if a new failing repro appears
    <!-- PATCHOPS_CONTENT_PATH_HANDOFF:END -->
    """
).strip()

next_prompt_block = textwrap.dedent(
    """
    [content_path repair stream]
    - The wrapper-relative content_path bug is already repaired and green through CP5.
    - Relative content_path values resolve from the wrapper project root first.
    - Manifest-local resolution remains compatibility fallback rather than the primary contract.
    - Do not reopen this area unless new contrary repo evidence appears.
    """
).strip()

if "<!-- PATCHOPS_CONTENT_PATH_HANDOFF:START -->" not in handoff_md_current:
    if handoff_md_current and not handoff_md_current.endswith("\n"):
        handoff_md_current += "\n"
    handoff_md_updated = handoff_md_current + ("\n" if handoff_md_current else "") + handoff_md_block + "\n"
else:
    start = "<!-- PATCHOPS_CONTENT_PATH_HANDOFF:START -->"
    end = "<!-- PATCHOPS_CONTENT_PATH_HANDOFF:END -->"
    before = handoff_md_current.split(start, 1)[0]
    after = handoff_md_current.split(end, 1)[1]
    handoff_md_updated = before + handoff_md_block + after

handoff_json_current["content_path_repair_stream"] = {
    "status": "green_through_cp5",
    "bug_state": "repaired",
    "resolution_rule": "wrapper_root_first",
    "fallback_rule": "manifest_local_compatibility_fallback",
    "example_apply_flow_proof": True,
    "next_posture": "maintenance_locked_do_not_reopen_without_new_contrary_evidence",
}

if "[content_path repair stream]" not in next_prompt_current:
    if next_prompt_current and not next_prompt_current.endswith("\n"):
        next_prompt_current += "\n"
    next_prompt_updated = next_prompt_current + ("\n" if next_prompt_current else "") + next_prompt_block + "\n"
else:
    marker = "[content_path repair stream]"
    before = next_prompt_current.split(marker, 1)[0]
    next_prompt_updated = before + next_prompt_block + "\n"

test_content = textwrap.dedent(
    """
    from __future__ import annotations

    import json
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_current_handoff_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "handoff" / "current_handoff.md").read_text(encoding="utf-8")
        assert "## content_path repair stream" in content
        assert "green through CP5" in content
        assert "wrapper project root first" in content
        assert "compatibility fallback" in content
        assert "Do not reopen" not in content  # prompt wording belongs in next_prompt, not current_handoff


    def test_current_handoff_json_mentions_content_path_repair_stream() -> None:
        payload = json.loads((PROJECT_ROOT / "handoff" / "current_handoff.json").read_text(encoding="utf-8"))
        stream = payload["content_path_repair_stream"]
        assert stream["status"] == "green_through_cp5"
        assert stream["bug_state"] == "repaired"
        assert stream["resolution_rule"] == "wrapper_root_first"
        assert stream["fallback_rule"] == "manifest_local_compatibility_fallback"
        assert stream["example_apply_flow_proof"] is True


    def test_next_prompt_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "handoff" / "next_prompt.txt").read_text(encoding="utf-8")
        assert "[content_path repair stream]" in content
        assert "wrapper project root first" in content
        assert "compatibility fallback rather than the primary contract" in content
        assert "Do not reopen this area unless new contrary repo evidence appears." in content
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
            "path": "handoff/current_handoff.md",
            "content": handoff_md_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "handoff/current_handoff.json",
            "content": json.dumps(handoff_json_current, indent=2),
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "handoff/next_prompt.txt",
            "content": next_prompt_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_path_handoff_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_handoff_refresh",
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
    "tags": ["content_path", "handoff", "docs_stop", "contract_lock"],
    "notes": (
        "Sixth repair-stream patch. "
        "This patch refreshes the maintained handoff surfaces so future continuation does not reopen the repaired content_path bug."
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
    "handoff_md_path": str(handoff_md_path),
    "handoff_json_path": str(handoff_json_path),
    "next_prompt_path": str(next_prompt_path),
    "test_path": str(test_path),
}))