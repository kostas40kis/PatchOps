from __future__ import annotations

from pathlib import Path

VALIDATE_PATH = Path("scripts/patch_l5_31_brief_validate.py")
PATCH_WRITER_PATH = Path("scripts/patch_l5_31_wire_edge_profile_parent_preflight_aggregate_cli_readback.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback.md")

FIXED_VALIDATE = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_31_candidate"
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
        payload = readback.build_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(f"PASS {name}: patch={payload['patch']} source={payload['source_l5_30_summary']['patch']} status={payload['status']}")

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
    print("PASS L5.31a brief validation: no Selenium/browser/profile/click/download/paste/send/package-run side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

DOC_NOTE = """

## L5.31a brief validator import-path repair

L5.31a repairs the L5.31 brief validator. Running `python scripts/patch_l5_31_brief_validate.py` places `scripts/` on `sys.path`, so the local `patchops` package was not importable. The repair inserts the repository root into `sys.path` before importing PatchOps modules.

The successful-report-size improvement remains: the validator parses JSON internally and prints only short PASS lines instead of echoing full nested payloads.

If accepted, continue with:

`L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint`
"""


def _patch_writer_template_if_present() -> None:
    if not PATCH_WRITER_PATH.exists():
        return
    text = PATCH_WRITER_PATH.read_text(encoding="utf-8")
    old = """import json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nfrom patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback as readback\n\nROOT = Path(__file__).resolve().parents[1]\n"""
    new = """import json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nif str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))\n\nfrom patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback as readback\n"""
    if old in text:
        text = text.replace(old, new, 1)
        PATCH_WRITER_PATH.write_text(text, encoding="utf-8")
        print("L5.31a patched embedded validator template in L5.31 writer")
    elif "if str(ROOT) not in sys.path:" in text:
        print("L5.31a embedded validator template already contains repo-root sys.path repair")
    else:
        print("L5.31a could not find embedded template; fixed standalone validator only")


def main() -> int:
    VALIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATE_PATH.write_text(FIXED_VALIDATE, encoding="utf-8")
    print("L5.31a wrote fixed brief validator with repo-root sys.path repair")

    _patch_writer_template_if_present()

    if DOC_PATH.exists():
        text = DOC_PATH.read_text(encoding="utf-8")
        if "## L5.31a brief validator import-path repair" not in text:
            DOC_PATH.write_text(text.rstrip() + DOC_NOTE, encoding="utf-8")
            print("L5.31a documentation repair note appended")
        else:
            print("L5.31a documentation repair note already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())