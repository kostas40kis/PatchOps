from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_aggregate_gate as aggregate

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-aggregate-gate"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l12_05_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l12_execution_preflight_chain_accepted"] is True
    assert payload["edge_executable_filesystem_probe_execution_preflight_aggregate_gate_enforced"] is True
    assert payload["execution_preflight_execution_allowed"] is False
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
    assert "source_l12_04_summary" not in payload


def main() -> int:
    no_gates = aggregate.build_edge_executable_filesystem_probe_execution_preflight_aggregate_gate(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False)
    assert_passive(no_gates)
    assert no_gates["execution_preflight_ready"] is False
    print("PASS no_gates: patch=L12.5 chain=True aggregate=True exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    execution_flag_only = aggregate.build_edge_executable_filesystem_probe_execution_preflight_aggregate_gate(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True)
    assert_passive(execution_flag_only)
    assert execution_flag_only["execution_preflight_ready"] is False
    print("PASS execution_flag_only: chain=True aggregate=True exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    real_ready_without_execution = aggregate.build_edge_executable_filesystem_probe_execution_preflight_aggregate_gate(ROOT, allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False)
    assert_passive(real_ready_without_execution)
    assert real_ready_without_execution["real_filesystem_probe_preflight_ready"] is True
    assert real_ready_without_execution["execution_preflight_ready"] is False
    print("PASS real_ready_without_execution_flag: chain=True aggregate=True real_ready=True exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    for name, profile in [("execution_preflight_ready_dedicated", DEDICATED), ("execution_preflight_ready_default", DEFAULT), ("execution_preflight_ready_missing_profile", None)]:
        payload = aggregate.build_edge_executable_filesystem_probe_execution_preflight_aggregate_gate(
            ROOT,
            allow_live_start=True,
            profile_dir=profile,
            allow_executable_probe=True,
            activate_executable_filesystem_probe=True,
            allow_real_filesystem_probe=True,
            allow_executable_filesystem_probe_execution=True,
        )
        assert_passive(payload)
        assert payload["execution_preflight_ready"] is True
        print("PASS {0}: patch=L12.5 source=L12.4 fixtures=6 exec_ready=True exec_allowed=False fs_probe=False path_selected=False".format(name))

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
            "--allow-executable-filesystem-probe-execution",
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
    print("PASS main_cli: compact JSON parsed quickly; execution-preflight aggregate gate stayed passive")
    print("PASS L12.5 brief validation: execution-preflight aggregate gate accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
