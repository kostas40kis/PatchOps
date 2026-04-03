from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_bootstrap_target_cli_current_module_invocation(tmp_path: Path) -> None:
    target_root = tmp_path / "demo_target"
    target_root.mkdir(parents=True, exist_ok=True)

    wrapper_root = tmp_path / "wrapper_root"
    wrapper_root.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "patchops.cli",
        "bootstrap-target",
        "--project-name",
        "Demo Bootstrap CLI",
        "--target-root",
        str(target_root),
        "--profile",
        "generic_python",
        "--wrapper-root",
        str(wrapper_root),
        "--initial-goal",
        "Create the first packet",
        "--initial-goal",
        "Generate the safest starter manifest",
    ]

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    onboarding_root = wrapper_root / "onboarding"
    bootstrap_md = onboarding_root / "current_target_bootstrap.md"
    bootstrap_json = onboarding_root / "current_target_bootstrap.json"
    next_prompt = onboarding_root / "next_prompt.txt"
    starter_manifest = onboarding_root / "starter_manifest.json"

    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()

    payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert payload["project_name"] == "Demo Bootstrap CLI"
    assert payload["written"] is True
    assert payload["selected_profile"] == "generic_python"
    assert Path(payload["bootstrap_markdown_path"]) == bootstrap_md.resolve()
    assert Path(payload["bootstrap_json_path"]) == bootstrap_json.resolve()
    assert Path(payload["next_prompt_path"]) == next_prompt.resolve()
    assert Path(payload["starter_manifest_path"]) == starter_manifest.resolve()
