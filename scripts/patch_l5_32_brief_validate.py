from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint as checkpoint

COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-broad-validation-checkpoint"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_32_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_parent_directory_created"] is False
    assert payload["profile_parent_filesystem_probe_performed"] is False
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
        payload = checkpoint.build_edge_supervised_launch_profile_parent_preflight_broad_validation_checkpoint(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} chain=L5.28/L5.29/L5.30/L5.31 status={2}".format(
                name,
                payload["patch"],
                payload["status"],
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
    print("PASS L5.32 brief validation: broad checkpoint accepted with no browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
