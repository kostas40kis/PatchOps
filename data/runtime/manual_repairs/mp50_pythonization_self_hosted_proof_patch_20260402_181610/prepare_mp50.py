from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path


MARKER = "Pythonization self-hosted proof is now exercised through PatchOps itself."
DETAIL = "This proof uses check, inspect, plan, and apply against PatchOps itself while keeping the repo changes narrow and maintenance-facing."


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def print_kv(key: str, value: object) -> None:
    print(f"{key}={value}")


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_root = working_root / "inner_reports"
    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    status_path = repo_root / "docs" / "project_status.md"
    test_path = repo_root / "tests" / "test_pythonization_self_hosted_proof_current.py"
    if not status_path.exists():
        raise SystemExit("docs/project_status.md not found.")

    status_text = status_path.read_text(encoding="utf-8")
    test_exists = test_path.exists()
    already_present = MARKER in status_text and test_exists

    if already_present:
        print_kv("decision", "stop_mp50_already_present")
        print_kv("manifest_path", "")
        print_kv("inner_report_root", str(inner_report_root))
        return 0

    updated_status = status_text
    addition = textwrap.dedent(
        f"""

        ## Pythonization self-hosted proof

        {MARKER}
        {DETAIL}
        """
    ).strip() + "\n"
    if MARKER not in updated_status:
        updated_status = updated_status.rstrip() + "\n\n" + addition

    out_status = content_root / "docs" / "project_status.md"
    ensure_parent(out_status)
    out_status.write_text(updated_status, encoding="utf-8")

    test_text = textwrap.dedent(
        f'''from pathlib import Path


def test_pythonization_self_hosted_proof_note_present() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8")
    assert {MARKER!r} in text
    assert {DETAIL!r} in text
'''
    )
    out_test = content_root / "tests" / "test_pythonization_self_hosted_proof_current.py"
    ensure_parent(out_test)
    out_test.write_text(test_text, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp50_pythonization_self_hosted_proof_patch",
        "active_profile": "generic_python",
        "target_project_root": str(repo_root),
        "files_to_write": [
            {
                "path": "docs/project_status.md",
                "content_path": str(out_status.resolve()),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_pythonization_self_hosted_proof_current.py",
                "content_path": str(out_test.resolve()),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "mp50 self-hosted proof tests",
                "program": "py",
                "args": [
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_pythonization_self_hosted_proof_current.py",
                ],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_root.resolve()),
            "report_name_prefix": "mp50",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp50", "self_hosted"],
        "notes": "MP50 self-hosted proof patch for the Pythonization stream.",
    }
    manifest_path = working_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print_kv("decision", "author_mp50")
    print_kv("manifest_path", str(manifest_path.resolve()))
    print_kv("inner_report_root", str(inner_report_root.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())