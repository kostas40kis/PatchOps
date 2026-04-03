from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp24_backup_write_evidence_integration_proof"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        from patchops.workflows.apply_patch import apply_manifest


        def _build_manifest(target_root: Path, report_dir: Path, files_to_write: list[dict[str, object]], patch_name: str) -> dict[str, object]:
            return {
                "manifest_version": "1",
                "patch_name": patch_name,
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": files_to_write,
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": patch_name,
                    "write_to_desktop": False,
                },
            }


        def test_apply_manifest_report_matches_backup_and_write_for_existing_target(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_root.mkdir(parents=True, exist_ok=True)
            manifest_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            destination = target_root / "docs" / "existing.txt"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("old payload", encoding="utf-8")

            manifest_path = manifest_root / "patch_manifest.json"
            manifest = _build_manifest(
                target_root,
                report_dir,
                [
                    {
                        "path": "docs/existing.txt",
                        "content": "new payload",
                        "content_path": None,
                        "encoding": "utf-8",
                    }
                ],
                "mp24_existing_backup_write_alignment",
            )
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            assert result.result_label == "PASS"
            assert destination.read_text(encoding="utf-8") == "new payload"

            backup_path = result.backup_root / "docs" / "existing.txt"
            assert backup_path.exists()
            assert backup_path.read_text(encoding="utf-8") == "old payload"

            report_text = result.report_path.read_text(encoding="utf-8")
            assert f"BACKUP : {destination} -> {backup_path}" in report_text
            assert f"WROTE : {destination}" in report_text


        def test_apply_manifest_report_marks_missing_and_write_for_new_target(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_root.mkdir(parents=True, exist_ok=True)
            manifest_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            destination = target_root / "docs" / "new.txt"

            manifest_path = manifest_root / "patch_manifest.json"
            manifest = _build_manifest(
                target_root,
                report_dir,
                [
                    {
                        "path": "docs/new.txt",
                        "content": "created by proof",
                        "content_path": None,
                        "encoding": "utf-8",
                    }
                ],
                "mp24_missing_backup_write_alignment",
            )
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            assert result.result_label == "PASS"
            assert destination.exists()
            assert destination.read_text(encoding="utf-8") == "created by proof"

            report_text = result.report_path.read_text(encoding="utf-8")
            assert f"MISSING: {destination}" in report_text
            assert f"WROTE : {destination}" in report_text
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    proof_test_path = wrapper_root / "tests" / "test_backup_write_evidence_integration_current.py"
    proof_test_exists_before = proof_test_path.exists()

    staged = {
        "tests/test_backup_write_evidence_integration_current.py": build_test_text(),
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
            "report_name_prefix": "mp24",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp24", "proof", "self_hosted"],
        "notes": "Prove that backup evidence and write evidence in the canonical report match actual file behavior for existing and missing targets.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "proof_test_path": str(proof_test_path),
        "proof_test_exists_before": proof_test_exists_before,
        "manifest_path": str(manifest_path),
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\n")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())