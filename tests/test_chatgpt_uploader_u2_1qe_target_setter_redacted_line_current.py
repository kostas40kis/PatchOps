from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_u2_1qe_target_setter_prints_legacy_redacted_line(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"
    config_path = tmp_path / "target.json"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            "https://chatgpt.com",
            "--mode",
            "operator_set",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "TARGET_CONFIG_WRITTEN:" in result.stdout
    assert "TARGET_URL_REDACTED: https://chatgpt.com/" in result.stdout
    assert str(config_path.resolve()) in result.stdout
