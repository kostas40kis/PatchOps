from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_real_probe_preflight_contract as preflight

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-contract"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l11_01_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l10_explicit_activation_stack_accepted"] is True
    assert payload["edge_executable_filesystem_probe_real_probe_preflight_contract_enforced"] is True
    assert payload["real_filesystem_probe_execution_allowed"] is False
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
    assert "source_l10_08_summary" not in payload


def main() -> int:
    no_real_flag = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(ROOT, allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=False)
    assert_passive(no_real_flag)
    assert no_real_flag["filesystem_probe_activation_ready"] is True
    assert no_real_flag["real_filesystem_probe_preflight_ready"] is False
    print("PASS no_real_flag: patch=L11.1 source=L10.8 activation_ready=True real_ready=False real_exec=False fs_probe=False path_selected=False")

    real_flag_only = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=True)
    assert_passive(real_flag_only)
    assert real_flag_only["real_filesystem_probe_preflight_ready"] is False
    print("PASS real_flag_only: activation_ready=False real_ready=False real_exec=False fs_probe=False path_selected=False")

    for name, profile in [("all_gates_dedicated", DEDICATED), ("all_gates_default", DEFAULT), ("all_gates_missing_profile", None)]:
        payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(
            ROOT,
            allow_live_start=True,
            profile_dir=profile,
            allow_executable_probe=True,
            activate_executable_filesystem_probe=True,
            allow_real_filesystem_probe=True,
        )
        assert_passive(payload)
        assert payload["filesystem_probe_activation_ready"] is True
        assert payload["real_filesystem_probe_preflight_ready"] is True
        print("PASS {0}: patch=L11.1 real_ready=True real_exec=False fs_probe=False path_selected=False".format(name))

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
            "--activate-executable-filesystem-probe",
            "--allow-real-filesystem-probe",
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
    print("PASS main_cli: compact JSON parsed quickly; real-probe preflight contract stayed passive")
    print("PASS L11.1 brief validation: real-probe preflight contract accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
