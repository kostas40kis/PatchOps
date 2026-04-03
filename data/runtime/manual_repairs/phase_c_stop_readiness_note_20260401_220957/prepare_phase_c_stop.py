from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "phase_c_stop_readiness_note"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_doc_text() -> str:
    return textwrap.dedent(
        """
        # Phase C stop â€” backup and write consolidation readiness

        This note records the maintained repo truth after the Phase C backup/write consolidation stream.

        ## What Phase C set out to do

        Phase C was the backup and file-write engine consolidation stream.

        The goal was to replace repeated backup and write choreography with reusable Python-owned planning and execution helpers while keeping PowerShell thin and preserving current manifest semantics.

        ## What landed

        The following landed green in this stream:

        - MP21 â€” single-file writer helper
        - MP22 â€” batch write orchestration
        - MP23 â€” content-path contract proof
        - MP24 â€” backup/write evidence integration proof
        - MP25 â€” backup/write docs refresh

        ## What the repo should now be treated as

        The repo should now be treated as having:

        - a helper-owned single-file write path,
        - a helper-owned multi-file write path,
        - current content-path behavior locked by proof tests,
        - report evidence for backup and write behavior locked to actual file behavior,
        - one durable doc explaining the helper-owned file-mechanics preference.

        ## Required checks for this stop

        The maintained Phase C stop requires:

        - backup tests green,
        - write tests green,
        - content-path contract tests green,
        - integration proof green.

        This stop exists to record that those checks were satisfied in the current stream before moving to the next trust layer.

        ## What comes next

        The next trust layer is Phase D â€” wrapper-exercised proof.

        The next planned patch after this stop is:

        - MP26 â€” run-origin metadata model

        That next layer should focus on proving, in reusable metadata and report surfaces, that the wrapper engine was actually the path that executed the run.

        ## What this stop does not do

        This stop does not reopen architecture and does not introduce new product identity.

        It only records that backup/write consolidation is green enough to support the next proof layer.
        """
    ).strip() + "\n"

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def test_phase_c_stop_readiness_note_records_green_backup_write_consolidation() -> None:
            doc_path = PROJECT_ROOT / "docs" / "phase_c_backup_write_readiness.md"
            content = doc_path.read_text(encoding="utf-8")

            assert "Phase C was the backup and file-write engine consolidation stream." in content
            assert "MP21 â€” single-file writer helper" in content
            assert "MP22 â€” batch write orchestration" in content
            assert "MP23 â€” content-path contract proof" in content
            assert "MP24 â€” backup/write evidence integration proof" in content
            assert "MP25 â€” backup/write docs refresh" in content
            assert "backup tests green" in content
            assert "write tests green" in content
            assert "content-path contract tests green" in content
            assert "integration proof green" in content
            assert "The next trust layer is Phase D â€” wrapper-exercised proof." in content
            assert "MP26 â€” run-origin metadata model" in content
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    doc_path = wrapper_root / "docs" / "phase_c_backup_write_readiness.md"
    test_path = wrapper_root / "tests" / "test_phase_c_backup_write_readiness_current.py"

    doc_exists_before = doc_path.exists()
    test_exists_before = test_path.exists()

    staged = {
        "docs/phase_c_backup_write_readiness.md": build_doc_text(),
        "tests/test_phase_c_backup_write_readiness_current.py": build_test_text(),
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
            "report_name_prefix": "phase_c_stop",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "phase_c_stop", "docs", "self_hosted"],
        "notes": "Record the Phase C stop truth and point continuation at Phase D wrapper-exercised proof without widening product claims.",
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