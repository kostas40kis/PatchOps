from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l10_06_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l10_05_explicit_activation_aggregate_gate_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback_enforced"] is True
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["fixture_activation_execution_allowed"] is False
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
    assert "source_l10_05_summary" not in payload


def main() -> int:
    no_activation = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False)
    assert_passive(no_activation)
    assert no_activation["filesystem_probe_activation_ready"] is False
    print("PASS no_activation: patch=L10.6 source=L10.5 chain=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    activation_only = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=True)
    assert_passive(activation_only)
    assert activation_only["filesystem_probe_activation_ready"] is False
    print("PASS activation_only: chain=True aggregate_readback=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    partial = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(ROOT, allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=False)
    assert_passive(partial)
    assert partial["filesystem_probe_activation_ready"] is False
    print("PASS live_and_probe_auth_without_activation: chain=True aggregate_readback=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    for name, profile in [("all_gates_dedicated", DEDICATED), ("all_gates_default", DEFAULT), ("all_gates_missing_profile", None)]:
        payload = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(
            ROOT,
            allow_live_start=True,
            profile_dir=profile,
            allow_executable_probe=True,
            activate_executable_filesystem_probe=True,
        )
        assert_passive(payload)
        assert payload["filesystem_probe_activation_ready"] is True
        print("PASS {0}: patch=L10.6 source=L10.5 fixtures=6 activation_ready=True activation_exec=False fs_probe=False path_selected=False".format(name))

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
    print("PASS main_cli: compact JSON parsed quickly; activation aggregate gate CLI/readback stayed passive")
    print("PASS L10.6 brief validation: activation aggregate gate CLI/readback accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
