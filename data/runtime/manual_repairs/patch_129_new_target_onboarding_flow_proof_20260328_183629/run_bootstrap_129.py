from __future__ import annotations

import json
from pathlib import Path

from patchops.project_packets import build_onboarding_bootstrap


PROJECT_ROOT = Path(r"C:\dev\patchops")
DEMO_PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "demo_roundtrip_current.md"
CAPTURE_PATH = Path(r"C:\\dev\\patchops\\data\\runtime\\manual_repairs\\patch_129_new_target_onboarding_flow_proof_20260328_183629\\bootstrap_payload.json")
TARGET_ROOT = r"C:\\dev\\patchops\\data\\runtime\\manual_repairs\\patch_129_new_target_onboarding_flow_proof_20260328_183629\\demo_roundtrip_current_target"


def main() -> int:
    payload = build_onboarding_bootstrap(
        project_name="Demo Roundtrip Current",
        target_root=TARGET_ROOT,
        profile_name="generic_python",
        wrapper_project_root=PROJECT_ROOT,
        packet_path=str(DEMO_PACKET_PATH),
        initial_goals=[
            "Create the current project packet",
            "Generate the safest starter manifest",
        ],
        current_stage="Initial onboarding",
    )
    CAPTURE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
