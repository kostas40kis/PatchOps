from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_discovery_fixture_matrix_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-discovery-fixture-matrix-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_04_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["edge_executable_fixture_matrix_cli_readback_enforced"] is True
    assert payload["edge_executable_fixture_count"] >= 4
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["edge_executable_fixture_filesystem_probe_performed"] is False
    assert payload["edge_executable_fixture_path_selected"] is False
    assert payload["edge_executable_fixture_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []


def main() -> int:
    cases = [
        ("no_auth_dedicated", False, DEDICATED),
        ("auth_dedicated", True, DEDICATED),
        ("auth_default", True, DEFAULT),
        ("missing_profile", True, None),
    ]
    for name, allow, profile in cases:
        payload = readback.build_edge_executable_discovery_fixture_matrix_cli_readback(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} source=L6.3 fixtures={2} exe_probe={3}".format(
                name,
                payload["patch"],
                payload["edge_executable_fixture_count"],
                payload["edge_executable_fixture_filesystem_probe_performed"],
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
            "--json",
            "--compact",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed; full JSON intentionally not echoed")
    print("PASS L6.4 brief validation: fixture matrix CLI/readback accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
