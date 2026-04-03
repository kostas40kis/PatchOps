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

status_test_path = project_root / "tests/test_content_path_status_current.py"
closure_test_path = project_root / "tests/test_content_path_stream_closure_status_current.py"

status_test_content = textwrap.dedent(
    """
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_project_status_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
        lowered = content.lower()
        assert "## content_path wrapper-root repair stream" in lowered
        assert "wrapper project root first" in lowered
        assert "compatibility fallback" in lowered
        assert "example manifest now has an end-to-end apply-flow proof" in lowered


    def test_patch_ledger_mentions_content_path_repair_stream() -> None:
        content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
        lowered = content.lower()
        assert "## content_path wrapper-root repair stream" in lowered
        assert "### cp1 - current-state repro contract" in lowered
        assert "### cp2 - wrapper-root resolution repair" in lowered
        assert "### cp3 - docs and example alignment" in lowered
        assert "### cp4 - example apply-flow proof" in lowered
        assert "ordinary maintenance, not runtime redesign" in lowered
    """
).lstrip()

closure_test_content = textwrap.dedent(
    """
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_project_status_mentions_closed_content_path_stream() -> None:
        content = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
        lowered = content.lower()
        assert "## content_path wrapper-root repair stream" in lowered
        assert "bug is repaired and the stream is complete" in lowered
        assert "handoff and onboarding surfaces now both carry the maintained content-path rule" in lowered
        assert "self-hosted windows powershell / ise authoring notes" in lowered
        assert "treat the content-path bug stream as closed unless new contrary repo evidence appears" in lowered


    def test_patch_ledger_mentions_cp5_through_cp9_and_closed_outcome() -> None:
        content = (PROJECT_ROOT / "docs" / "patch_ledger.md").read_text(encoding="utf-8")
        lowered = content.lower()
        assert "### cp5 - docs stop and status lock" in lowered
        assert "### cp6 - handoff refresh and lock" in lowered
        assert "### cp7 - onboarding refresh and lock" in lowered
        assert "### cp8 - finalization closure lock" in lowered
        assert "### cp9 - self-hosted authoring hardening notes" in lowered
        assert "green through cp9 and closed" in lowered
        assert "ordinary maintenance, not runtime redesign" in lowered
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
            "path": "tests/test_content_path_status_current.py",
            "content": status_test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_content_path_stream_closure_status_current.py",
            "content": closure_test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_status_test_contract_repair",
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
    "tags": ["content_path", "tests", "doc_contract", "narrow_repair"],
    "notes": (
        "CP10A narrow repair. "
        "This patch updates stale content_path status-surface tests so they match the newer closed-stream wording introduced by CP10."
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
    "status_test_path": str(status_test_path),
    "closure_test_path": str(closure_test_path),
}))