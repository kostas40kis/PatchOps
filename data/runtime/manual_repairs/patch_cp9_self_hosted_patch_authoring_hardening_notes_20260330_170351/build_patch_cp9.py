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

llm_usage_path = project_root / "docs/llm_usage.md"
compatibility_path = project_root / "docs/compatibility_notes.md"
test_path = project_root / "tests/test_self_hosted_patch_authoring_notes_current.py"

llm_usage_current = llm_usage_path.read_text(encoding="utf-8")
compatibility_current = compatibility_path.read_text(encoding="utf-8")

llm_usage_block = textwrap.dedent(
    """
    <!-- PATCHOPS_SELF_HOSTED_AUTHORING_NOTES:START -->
    ## Self-hosted patch authoring notes for Windows PowerShell / ISE

    When generating self-hosted PatchOps repair scripts that write a temporary patch manifest and then call PatchOps from Windows PowerShell 5.1 or PowerShell ISE, use this pattern:

    - write the patch manifest as compact JSON
    - do not add a trailing newline to the patch manifest
    - validate the manifest immediately with `json.load(...)` before calling PatchOps
    - if the PatchOps run fails early, print the manifest content for debugging
    - prefer `System.Diagnostics.ProcessStartInfo.Arguments` over `ArgumentList` in Windows PowerShell 5.1 / ISE compatibility mode

    These notes are not architecture changes.
    They are operator-authoring hardening notes that reduce avoidable script failures in self-hosted repair flows.
    <!-- PATCHOPS_SELF_HOSTED_AUTHORING_NOTES:END -->
    """
).strip()

compatibility_block = textwrap.dedent(
    """
    <!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:START -->
    ## Self-hosted manifest-authoring compatibility note

    In Windows PowerShell 5.1 / PowerShell ISE, generated self-hosted PatchOps scripts should avoid relying on `ProcessStartInfo.ArgumentList`.
    Use `ProcessStartInfo.Arguments` with careful argument escaping instead.

    For temporary self-hosted patch manifests, prefer:
    - compact JSON,
    - no trailing newline,
    - immediate `json.load(...)` validation before the apply step.

    This reduces false starts where the wrapper never reaches the real validation target because the authoring script itself failed first.
    <!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:END -->
    """
).strip()

if "<!-- PATCHOPS_SELF_HOSTED_AUTHORING_NOTES:START -->" not in llm_usage_current:
    if not llm_usage_current.endswith("\n"):
        llm_usage_current += "\n"
    llm_usage_updated = llm_usage_current + "\n" + llm_usage_block + "\n"
else:
    start = "<!-- PATCHOPS_SELF_HOSTED_AUTHORING_NOTES:START -->"
    end = "<!-- PATCHOPS_SELF_HOSTED_AUTHORING_NOTES:END -->"
    before = llm_usage_current.split(start, 1)[0]
    after = llm_usage_current.split(end, 1)[1]
    llm_usage_updated = before + llm_usage_block + after

if "<!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:START -->" not in compatibility_current:
    if not compatibility_current.endswith("\n"):
        compatibility_current += "\n"
    compatibility_updated = compatibility_current + "\n" + compatibility_block + "\n"
else:
    start = "<!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:START -->"
    end = "<!-- PATCHOPS_SELF_HOSTED_COMPAT_NOTES:END -->"
    before = compatibility_current.split(start, 1)[0]
    after = compatibility_current.split(end, 1)[1]
    compatibility_updated = before + compatibility_block + after

test_content = textwrap.dedent(
    """
    from pathlib import Path


    PROJECT_ROOT = Path(__file__).resolve().parents[1]


    def test_llm_usage_mentions_self_hosted_patch_authoring_notes() -> None:
        content = (PROJECT_ROOT / "docs" / "llm_usage.md").read_text(encoding="utf-8")
        assert "## Self-hosted patch authoring notes for Windows PowerShell / ISE" in content
        assert "write the patch manifest as compact JSON" in content
        assert "do not add a trailing newline to the patch manifest" in content
        assert "validate the manifest immediately with `json.load(...)`" in content
        assert "ProcessStartInfo.Arguments" in content
        assert "ArgumentList" in content


    def test_compatibility_notes_mentions_self_hosted_manifest_authoring_pattern() -> None:
        content = (PROJECT_ROOT / "docs" / "compatibility_notes.md").read_text(encoding="utf-8")
        assert "## Self-hosted manifest-authoring compatibility note" in content
        assert "PowerShell ISE" in content
        assert "avoid relying on `ProcessStartInfo.ArgumentList`" in content
        assert "compact JSON" in content
        assert "no trailing newline" in content
        assert "immediate `json.load(...)` validation" in content
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
            "path": "docs/llm_usage.md",
            "content": llm_usage_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/compatibility_notes.md",
            "content": compatibility_updated,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_self_hosted_patch_authoring_notes_current.py",
            "content": test_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_self_hosted_patch_authoring_hardening",
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
    "tags": ["self_hosted", "powershell_ise", "authoring", "compatibility", "contract_lock"],
    "notes": (
        "Ninth follow-up patch. "
        "This patch records the self-hosted authoring lessons from the content_path repair stream so future generated PowerShell / ISE scripts avoid the same avoidable failures."
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
    "llm_usage_path": str(llm_usage_path),
    "compatibility_path": str(compatibility_path),
    "test_path": str(test_path),
}))