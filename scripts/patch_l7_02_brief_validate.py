from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l7_02_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l7_01_executable_probe_authorization_contract_remains_accepted"] is True
    assert payload["edge_executable_probe_authorization_readback_enforced"] is True
    assert payload["edge_executable_probe_authorization_modeled"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    assert payload["authorization_alone_does_not_perform_probe"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l7_01_summary" not in payload


def main() -> int:
    cases = [
        ("no_probe_auth", False, DEDICATED, False),
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = readback.build_edge_executable_probe_authorization_cli_readback(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} source=L7.1 probe_authorized={2} probe_permitted={3} exe_probe={4}".format(
                name,
                payload["patch"],
                payload["edge_executable_probe_authorized"],
                payload["edge_executable_probe_permitted_by_phase"],
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
    print("PASS main_cli: compact JSON parsed quickly; executable probe authorization readback stayed passive")
    print("PASS L7.2 brief validation: probe authorization CLI/readback accepted with no executable probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
