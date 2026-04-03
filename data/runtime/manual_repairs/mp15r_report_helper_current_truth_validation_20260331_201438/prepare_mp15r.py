from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15r.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    rel_paths = [
        Path("patchops") / "reporting" / "sections.py",
        Path("patchops") / "reporting" / "command_sections.py",
    ]

    optional_paths = [
        Path("tests") / "test_reporting_output_helper_current.py",
    ]

    copied = []
    for rel in rel_paths + optional_paths:
        src = wrapper_root / rel
        if not src.exists():
            if rel in rel_paths:
                raise RuntimeError(f"Required file missing: {src}")
            continue
        dst = working_root / "content" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied.append(str(rel).replace('\\', '/'))

    validation_targets = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_reporting_output_helper_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
        "tests/test_required_vs_tolerated_report_current.py",
        "tests/test_summary_integrity_workflow_current.py",
    ]
    validation_targets = [t for t in validation_targets if (wrapper_root / Path(t)).exists()]

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp15r_report_helper_current_truth_validation",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace('\\', '/'),
        "backup_files": copied,
        "files_to_write": [
            {
                "path": rel,
                "content_path": f"content/{rel}",
                "encoding": "utf-8",
            }
            for rel in copied
        ],
        "validation_commands": [
            {
                "name": "report_helper_current_truth_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
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
            "report_dir": str((working_root / "inner_reports")).replace('\\', '/'),
            "report_name_prefix": "mp15r_report_helper_current_truth_validation",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "validation_only"],
        "notes": "Validation-only MP15 wrapper repair. Replays the current on-disk reporting surfaces through PatchOps apply after the fragile inline CLI smoke step was removed.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

    info_lines = [
        "decision=mp15r_current_truth_validation",
        f"manifest_path={manifest_path}",
        f"copied_files={';'.join(copied)}",
        f"validation_targets={';'.join(validation_targets)}",
        "rationale=The latest red was the wrapper's inline py -c smoke quoting, so the truthful next move is to validate the current on-disk repo state through check/inspect/plan/apply without another fragile smoke layer.",
    ]
    write_text(working_root / "prepare_info.txt", "\n".join(info_lines) + "\n")

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())