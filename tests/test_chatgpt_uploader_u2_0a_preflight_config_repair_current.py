from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _run_preflight(config_path: Path, evidence_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--evidence-dir",
            str(evidence_dir),
            "--no-real-edge",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_missing_target_config_writes_fail_or_blocked_evidence(tmp_path) -> None:
    missing_config = tmp_path / "missing" / "target.json"
    evidence_dir = tmp_path / "evidence_missing"
    result = _run_preflight(missing_config, evidence_dir)

    assert result.returncode == 2
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: FAIL_OR_BLOCKED" in result.stdout
    evidence_path = _json_evidence_path(result.stdout)
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL_OR_BLOCKED"
    assert payload["result_label"] == "FAIL_OR_BLOCKED"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert payload["events"][0]["event"] == "config_load_failed"


def test_seeded_target_config_allows_apply_time_config_only_smoke(tmp_path) -> None:
    config_path = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence_ok"
    set_result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            TARGET_URL,
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert set_result.returncode == 0, set_result.stderr

    result = _run_preflight(config_path, evidence_dir)
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS_CONFIG_ONLY" in result.stdout
    evidence_path = _json_evidence_path(result.stdout)
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_CONFIG_ONLY"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
