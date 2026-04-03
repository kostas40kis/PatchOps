from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp23_content_path_contract_proof"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        from patchops.files.writers import write_files
        from patchops.models import FileWriteSpec, WriteRecord
        from patchops.workflows.apply_patch import apply_manifest


        def test_write_files_prefers_wrapper_project_root_for_content_path(tmp_path: Path) -> None:
            target_root = tmp_path / "target"
            wrapper_root = tmp_path / "wrapper"
            manifest_root = tmp_path / "manifest_root"

            wrapper_content = wrapper_root / "content" / "docs" / "source.txt"
            manifest_content = manifest_root / "content" / "docs" / "source.txt"
            wrapper_content.parent.mkdir(parents=True, exist_ok=True)
            manifest_content.parent.mkdir(parents=True, exist_ok=True)
            wrapper_content.write_text("wrapper-root-wins", encoding="utf-8")
            manifest_content.write_text("manifest-local-loses", encoding="utf-8")

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")

            spec = FileWriteSpec(
                path="docs/out.txt",
                content=None,
                content_path="content/docs/source.txt",
                encoding="utf-8",
            )

            records = write_files(
                [spec],
                target_root,
                manifest_path=manifest_path,
                wrapper_project_root=wrapper_root,
            )

            destination = target_root / "docs" / "out.txt"
            assert destination.read_text(encoding="utf-8") == "wrapper-root-wins"
            assert records == [WriteRecord(path=destination, encoding="utf-8")]


        def test_write_files_falls_back_to_manifest_local_content_path(tmp_path: Path) -> None:
            target_root = tmp_path / "target"
            wrapper_root = tmp_path / "wrapper"
            manifest_root = tmp_path / "manifest_root"

            manifest_content = manifest_root / "content" / "docs" / "source.txt"
            manifest_content.parent.mkdir(parents=True, exist_ok=True)
            manifest_content.write_text("manifest-local-fallback", encoding="utf-8")

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")

            spec = FileWriteSpec(
                path="docs/out.txt",
                content=None,
                content_path="content/docs/source.txt",
                encoding="utf-8",
            )

            records = write_files(
                [spec],
                target_root,
                manifest_path=manifest_path,
                wrapper_project_root=wrapper_root,
            )

            destination = target_root / "docs" / "out.txt"
            assert destination.read_text(encoding="utf-8") == "manifest-local-fallback"
            assert records == [WriteRecord(path=destination, encoding="utf-8")]


        def test_apply_manifest_preserves_wrapper_root_first_content_path_contract(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper_root"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_content = wrapper_root / "content" / "payloads" / "demo.txt"
            manifest_content = manifest_root / "content" / "payloads" / "demo.txt"
            wrapper_content.parent.mkdir(parents=True, exist_ok=True)
            manifest_content.parent.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            wrapper_content.write_text("wrapper-apply-wins", encoding="utf-8")
            manifest_content.write_text("manifest-apply-loses", encoding="utf-8")

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp23_wrapper_root_first_apply_contract",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [
                    {
                        "path": "docs/result.txt",
                        "content": None,
                        "content_path": "content/payloads/demo.txt",
                        "encoding": "utf-8",
                    }
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp23_apply_contract",
                    "write_to_desktop": False,
                },
            }
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            destination = target_root / "docs" / "result.txt"
            assert result.result_label == "PASS"
            assert destination.read_text(encoding="utf-8") == "wrapper-apply-wins"


        def test_apply_manifest_keeps_manifest_local_content_path_fallback(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper_root"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            manifest_content = manifest_root / "content" / "payloads" / "demo.txt"
            manifest_content.parent.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest_content.write_text("manifest-apply-fallback", encoding="utf-8")

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp23_manifest_local_apply_fallback",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [
                    {
                        "path": "docs/result.txt",
                        "content": None,
                        "content_path": "content/payloads/demo.txt",
                        "encoding": "utf-8",
                    }
                ],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp23_apply_fallback",
                    "write_to_desktop": False,
                },
            }
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            destination = target_root / "docs" / "result.txt"
            assert result.result_label == "PASS"
            assert destination.read_text(encoding="utf-8") == "manifest-apply-fallback"
        """
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    writers_path = wrapper_root / "patchops" / "files" / "writers.py"
    apply_path = wrapper_root / "patchops" / "workflows" / "apply_patch.py"
    proof_test_path = wrapper_root / "tests" / "test_content_path_contract_proof_current.py"

    writers_source = writers_path.read_text(encoding="utf-8")
    apply_source = apply_path.read_text(encoding="utf-8")

    write_files_exists_before = "def write_files(" in writers_source
    apply_uses_write_files_before = "write_files(" in apply_source
    proof_test_exists_before = proof_test_path.exists()

    test_text = build_test_text()

    staged = {
        "tests/test_content_path_contract_proof_current.py": test_text,
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
            "report_name_prefix": "mp23",
            "write_to_desktop": False,
        },
        "tags": ["pythonization", "mp23", "proof", "self_hosted"],
        "notes": "Prove that the content_path contract still holds through write_files and apply_manifest: wrapper-root first with manifest-local compatibility fallback.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
    json.loads(manifest_path.read_text(encoding="utf-8"))

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "apply_path": str(apply_path),
        "proof_test_path": str(proof_test_path),
        "write_files_exists_before": write_files_exists_before,
        "apply_uses_write_files_before": apply_uses_write_files_before,
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