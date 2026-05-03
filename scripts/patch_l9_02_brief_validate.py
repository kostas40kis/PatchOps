from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l9_02_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l9_01_executable_filesystem_probe_passive_contract_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_cli_readback_enforced"] is True
    assert payload["edge_executable_filesystem_probe_contract_enforced"] is True
    assert payload["edge_executable_candidate_path_labels_modeled"] is True
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l9_01_summary" not in payload


def main() -> int:
    no_auth = readback.build_edge_executable_filesystem_probe_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False)
    assert_passive(no_auth)
    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False
    assert no_auth["edge_executable_filesystem_probe_contract_ready"] is False
    print("PASS no_probe_auth: patch=L9.2 readback_ok=True preflight_passed=False contract_ready=False fs_probe=False path_selected=False")

    cases = [
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = readback.build_edge_executable_filesystem_probe_cli_readback(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        assert payload["edge_executable_probe_safety_preflight_passed"] is True
        assert payload["edge_executable_filesystem_probe_contract_ready"] is True
        print(
            "PASS {0}: patch={1} source=L9.1 preflight_passed={2} contract_ready={3} fs_probe={4} path_selected={5}".format(
                name,
                payload["patch"],
                payload["edge_executable_probe_safety_preflight_passed"],
                payload["edge_executable_filesystem_probe_contract_ready"],
                payload["edge_executable_filesystem_probe_performed"],
                payload["edge_executable_path_selected"],
            )
        )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED),
            "--allow-executable-probe",
            "--json",
            "--compact",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert len(completed.stdout) < 80000
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed quickly; filesystem probe CLI/readback stayed passive")
    print("PASS L9.2 brief validation: executable filesystem probe CLI/readback accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
