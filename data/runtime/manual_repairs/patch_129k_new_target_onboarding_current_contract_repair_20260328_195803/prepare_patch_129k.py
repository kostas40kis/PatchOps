from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    manifest_path = Path(sys.argv[2]).resolve()
    content_path = Path(sys.argv[3]).resolve()
    work_root = Path(sys.argv[4]).resolve()

    project_packets_path = repo_root / "patchops" / "project_packets.py"
    baseline_test_path = repo_root / "tests" / "test_project_packet_onboarding_bootstrap.py"
    status_doc_path = repo_root / "docs" / "project_status.md"

    project_packets_text = project_packets_path.read_text(encoding="utf-8")
    baseline_test_text = baseline_test_path.read_text(encoding="utf-8")
    status_text = status_doc_path.read_text(encoding="utf-8") if status_doc_path.exists() else ""

    evidence_checks = {
        "build_onboarding_bootstrap surface": "build_onboarding_bootstrap" in project_packets_text,
        "baseline written contract": 'payload["written"] is True' in baseline_test_text,
        "baseline bootstrap_json_path contract": 'bootstrap_json_path' in baseline_test_text,
    }
    missing = [name for name, ok in evidence_checks.items() if not ok]
    if missing:
        raise SystemExit(
            "Repo evidence does not match the expected narrow Patch 94C-style repair posture. "
            "Missing markers: " + ", ".join(missing)
        )

    test_content = """from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import build_onboarding_bootstrap


def _read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_current_onboarding_bootstrap_payload_matches_demo_target(capsys, tmp_path) -> None:
    wrapper_root = tmp_path

    direct_payload = build_onboarding_bootstrap(
        project_name="Demo Target",
        target_root=r"C:\\\\dev\\\\demo_target",
        profile_name="generic_python",
        wrapper_project_root=wrapper_root,
        initial_goals=["Create the packet", "Run check inspect and plan"],
    )
    expected_json = _read_json(direct_payload["bootstrap_json_path"])

    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Demo Target",
            "--target-root",
            r"C:\\\\dev\\\\demo_target",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(wrapper_root),
            "--initial-goal",
            "Create the packet",
            "--initial-goal",
            "Run check inspect and plan",
        ]
    )

    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    actual_json = _read_json(cli_payload["bootstrap_json_path"])

    assert cli_payload["written"] is True
    assert cli_payload["project_name"] == "Demo Target"
    assert Path(cli_payload["bootstrap_markdown_path"]).exists()
    assert Path(cli_payload["bootstrap_json_path"]).exists()
    assert Path(cli_payload["next_prompt_path"]).exists()
    assert Path(cli_payload["starter_manifest_path"]).exists()

    assert actual_json == expected_json
    assert actual_json["project_name"] == "Demo Target"
    assert actual_json["profile_name"] == "generic_python"

    md_text = Path(cli_payload["bootstrap_markdown_path"]).read_text(encoding="utf-8")
    assert "# Onboarding bootstrap - Demo Target" in md_text
    assert r"`C:\\\\dev\\\\demo_target`" in md_text

    next_prompt_text = Path(cli_payload["next_prompt_path"]).read_text(encoding="utf-8")
    assert "Demo Target" in next_prompt_text
    assert "generic_python" in next_prompt_text
"""

    content_path.parent.mkdir(parents=True, exist_ok=True)
    content_path.write_text(test_content, encoding="utf-8")

    content_rel = content_path.relative_to(repo_root)

    manifest = {
        "manifest_version": "1",
        "patch_name": "patch_129k_new_target_onboarding_current_contract_repair",
        "active_profile": "generic_python",
        "target_project_root": repo_root.as_posix(),
        "backup_files": [
            "tests/test_new_target_onboarding_current.py"
        ],
        "files_to_write": [
            {
                "path": "tests/test_new_target_onboarding_current.py",
                "content": None,
                "content_path": content_rel.as_posix(),
                "encoding": "utf-8"
            }
        ],
        "validation_commands": [
            {
                "name": "full_pytest",
                "program": "py",
                "args": ["-3", "-m", "pytest", "-q"],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0]
            }
        ],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((work_root / "reports").resolve()),
            "report_name_prefix": "patch_129k_new_target_onboarding_current_contract_repair",
            "write_to_desktop": False
        },
        "tags": [
            "self_hosted",
            "onboarding",
            "validation_repair",
            "f5"
        ],
        "notes": "Align the F5 current-onboarding proof test with the already-shipped onboarding bootstrap contract."
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "manifest_path": str(manifest_path),
        "content_path": str(content_path),
        "status_mentions_patch_94c": ("Patch 94C" in status_text and "current direct payload contract" in status_text),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())