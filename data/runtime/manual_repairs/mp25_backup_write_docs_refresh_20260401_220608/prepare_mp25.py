from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp25_backup_write_docs_refresh"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_doc_text() -> str:
    return textwrap.dedent(
        """
        # Backup and write mechanics

        This note explains the current PatchOps file-mechanics posture after the Pythonization Phase C work landed.

        ## What changed

        Backup and write mechanics are now **Python-owned reusable surfaces** rather than patch-body boilerplate.

        That means a maintenance patch should not keep re-implementing the same backup-copy rules, mkdir rules, content loading rules, or write-report formatting in each individual patch body.

        Instead, the shared helper path now owns those mechanics.

        ## The helper-owned path

        The maintained helper path is:

        - backup planning and backup execution stay in the Python file-mechanics layer,
        - write intent is normalized before execution,
        - single-file writes go through one deterministic helper,
        - batch writes go through one shared orchestration path,
        - canonical report lines come from the same helper-owned truth as the actual backup and write behavior.

        ## What contributors should do

        When a new patch needs to touch files:

        1. prefer the existing Python backup/write helpers,
        2. keep PowerShell thin and operator-facing,
        3. avoid rebuilding file choreography inside each patch body,
        4. keep report evidence aligned with actual helper behavior,
        5. preserve current manifest semantics and the maintained content-path contract.

        ## What this does not mean

        This docs refresh does **not** introduce a new product surface and does **not** redesign PatchOps.

        It only clarifies that the repetitive file mechanics now belong to reusable Python helpers instead of one-off patch boilerplate.

        ## Current maintained contract

        The current maintained contract for this area is:

        - helper-owned backup and write mechanics,
        - one canonical report path,
        - wrapper project root first for the maintained content-path rule,
        - manifest-local compatibility fallback where that legacy path still matters,
        - narrow proof patches preferred over broad rewrites.

        ## Contributor guidance

        If you are writing a new maintenance patch, start by asking:

        - is there already a helper for this backup/write step?
        - can I prove the behavior with a narrow test or proof patch instead of widening the design?
        - am I keeping PowerShell boring and the real mechanics in Python?

        If the answer is yes, stay on the helper-owned path.
        """
    ).strip() + "\n"

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def test_backup_write_mechanics_doc_guides_contributors_to_helper_path() -> None:
            doc_path = PROJECT_ROOT / "docs" / "backup_write_mechanics.md"
            content = doc_path.read_text(encoding="utf-8")

            assert "Python-owned reusable surfaces" in content
            assert "rather than patch-body boilerplate" in content
            assert "single-file writes go through one deterministic helper" in content
            assert "batch writes go through one shared orchestration path" in content
            assert "prefer the existing Python backup/write helpers" in content
            assert "keep PowerShell thin and operator-facing" in content
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    doc_path = wrapper_root / "docs" / "backup_write_mechanics.md"
    test_path = wrapper_root / "tests" / "test_backup_write_docs_refresh_current.py"

    doc_exists_before = doc_path.exists()
    test_exists_before = test_path.exists()

    staged = {
        "docs/backup_write_mechanics.md": build_doc_text(),
        "tests/test_backup_write_docs_refresh_current.py": build_test_text(),
    }

    files_to_write = []
    for relative_path, content in staged.items():
        staged_path = content_root / relative_path
        write_text(staged_path, content)
        files_to_write.append(
            {
                "path": relative_path,
                "content": None,
                "content_path": str(staged_path.relative_to(working_root)).replace("\\", "/"),
                "encoding": "utf-8",
            }
        )

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": list(staged.keys()),
        "files_to_write": files_to_write,
        "validation_commands": [
            {
                "name": "full-pytest-quiet",
                "program": "py",
                "args": ["-m", "pytest", "-q"],
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
            "report_dir": str((working_root / "inner_reports").resolve()),
            "report_name_prefix": "mp25",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp25", "docs", "self_hosted"],
        "notes": "Refresh one durable doc so contributors are guided toward the helper-owned backup/write path rather than patch-body boilerplate.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "doc_path": str(doc_path),
        "test_path": str(test_path),
        "doc_exists_before": doc_exists_before,
        "test_exists_before": test_exists_before,
        "manifest_path": str(manifest_path),
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())