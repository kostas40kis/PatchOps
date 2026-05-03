from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_fixture_matrix as matrix

COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-fixture-matrix"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l8_03_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l8_02_executable_probe_safety_preflight_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_probe_safety_preflight_fixture_matrix_enforced"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["preflight_alone_does_not_perform_probe"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_probe_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l8_02_summary" not in payload


def main() -> int:
    no_auth = matrix.build_edge_executable_probe_safety_preflight_fixture_matrix(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False)
    assert_passive(no_auth)
    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False
    print("PASS no_probe_auth: patch=L8.3 readback_ok=True preflight_passed=False fixtures=5 probe_execution_allowed=False exe_probe=False")

    cases = [
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = matrix.build_edge_executable_probe_safety_preflight_fixture_matrix(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        assert payload["edge_executable_probe_safety_preflight_passed"] is True
        print(
            "PASS {0}: patch={1} source=L8.2 fixtures={2} preflight_passed={3} probe_execution_allowed={4} exe_probe={5}".format(
                name,
                payload["patch"],
                payload["edge_executable_probe_safety_preflight_fixture_count"],
                payload["edge_executable_probe_safety_preflight_passed"],
                payload["edge_executable_probe_preflight_allows_probe_execution"],
                payload["edge_executable_filesystem_probe_performed"],
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
    print("PASS main_cli: compact JSON parsed quickly; safety preflight fixture matrix stayed passive")
    print("PASS L8.3 brief validation: safety preflight fixture matrix accepted with no executable probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
