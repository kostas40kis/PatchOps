from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_u2_1qf_resolve_config_path_aliases(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import (
        resolve_config_path,
        resolve_target_config_path,
        target_config_path,
    )

    explicit = tmp_path / "target.json"

    assert resolve_config_path(path=explicit) == explicit.resolve()
    assert resolve_config_path(config_path=explicit) == explicit.resolve()
    assert resolve_config_path(target_config=explicit) == explicit.resolve()
    assert resolve_config_path(PROJECT_ROOT, explicit) == explicit.resolve()
    assert resolve_target_config_path(PROJECT_ROOT, explicit) == explicit.resolve()
    assert target_config_path(PROJECT_ROOT, explicit) == explicit.resolve()

    defaulted = resolve_config_path(repo_root=PROJECT_ROOT)
    assert defaulted == (PROJECT_ROOT / "data" / "config" / "chatgpt_copilot_target.json").resolve()


def test_u2_1qf_dry_run_scripts_import_resolve_config_path(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")

    scripts = [
        PROJECT_ROOT / "scripts" / "run_uploader_type_path_enter_no_send.py",
        PROJECT_ROOT / "scripts" / "run_uploader_recover_edge_then_type_path_enter_no_send.py",
    ]

    for script in scripts:
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--repo-root",
                str(PROJECT_ROOT),
                "--report-path",
                str(report),
                "--evidence-dir",
                str(tmp_path / script.stem),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr
        combined = result.stdout + result.stderr
        assert "ImportError" not in combined
        assert "FILE_UPLOAD_ATTEMPTED: true" not in combined
        assert "CHATGPT_SUBMIT_PERFORMED: true" not in combined
