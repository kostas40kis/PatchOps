from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix as matrix

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_03_candidate"
EXISTING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_03.exe"
MISSING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-03.exe"


def assert_no_launch(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l13_02_execution_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_execution_fixture_matrix_enforced"] is True
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []


def candidate_for(payload: dict, path: Path) -> dict | None:
    expected = str(path)
    for item in payload.get("edge_executable_probe_candidates", []) or []:
        if item.get("path") == expected:
            return item
    return None


def assert_truthful_selection(payload: dict) -> None:
    selected = payload.get("edge_executable_selected_path")
    if payload["edge_executable_path_selected"]:
        assert any(
            item.get("path") == selected and item.get("exists") is True and item.get("is_file") is True
            for item in payload.get("edge_executable_probe_candidates", []) or []
        )
    else:
        assert selected is None


def main() -> int:
    for name, kwargs in [
        ("no_gates", dict(allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False)),
        ("execution_flag_only", dict(allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True)),
        ("real_ready_without_execution_flag", dict(allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False)),
    ]:
        payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(ROOT, extra_candidates=[str(MISSING_FIXTURE)], **kwargs)
        assert_no_launch(payload)
        assert payload["edge_executable_filesystem_probe_performed"] is False
        print("PASS {0}: patch=L13.3 fixtures=5 probe_performed=False path_selected=False launch=False".format(name))

    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    ready = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(
        ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE), str(EXISTING_FIXTURE)],
    )
    assert_no_launch(ready)
    assert ready["edge_executable_filesystem_probe_performed"] is True
    observed_fixture = candidate_for(ready, EXISTING_FIXTURE)
    assert observed_fixture is not None
    assert observed_fixture.get("exists") is True
    assert observed_fixture.get("is_file") is True
    assert_truthful_selection(ready)
    print("PASS execution_ready_fixture_observed: patch=L13.3 fixtures=5 probe_performed=True fixture_observed=True selected_path={0} launch=False".format(ready.get("edge_executable_selected_path") or "(none)"))

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
            "--extra-candidate",
            str(MISSING_FIXTURE),
            "--extra-candidate",
            str(EXISTING_FIXTURE),
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
    assert len(completed.stdout) < 95000
    assert_no_launch(payload)
    observed_fixture = candidate_for(payload, EXISTING_FIXTURE)
    assert observed_fixture is not None
    assert observed_fixture.get("exists") is True
    assert observed_fixture.get("is_file") is True
    assert_truthful_selection(payload)
    print("PASS main_cli: compact JSON parsed quickly; execution fixture matrix was truthful and launched nothing")
    print("PASS L13.3 brief validation: read-only executable filesystem probe execution fixture matrix accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
