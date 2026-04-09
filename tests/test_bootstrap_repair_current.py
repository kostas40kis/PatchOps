from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.bootstrap_repair import apply_bootstrap_repair


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_synthetic_broken_package(target_root: Path) -> None:
    package_root = target_root / "demo_pkg"
    package_root.mkdir(parents=True, exist_ok=True)
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "cli.py").write_text(
        "from demo_pkg.broken_mod import repaired\n\n"
        "def main() -> None:\n"
        "    print(repaired())\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8",
    )
    (package_root / "broken_mod.py").write_text(
        "def repaired(:\n"
        "    return 'broken'\n",
        encoding="utf-8",
    )


def _write_repair_payload(payload_root: Path) -> None:
    repair_path = payload_root / "demo_pkg" / "broken_mod.py"
    repair_path.parent.mkdir(parents=True, exist_ok=True)
    repair_path.write_text(
        "def repaired() -> str:\n"
        "    return 'repair-ok'\n",
        encoding="utf-8",
    )


def _run_synthetic_cli(target_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "demo_pkg.cli"],
        cwd=target_root,
        text=True,
        capture_output=True,
    )


def test_bootstrap_repair_restores_synthetic_import_chain_and_compiles(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    payload_root = tmp_path / "payload"
    target_root.mkdir(parents=True, exist_ok=True)
    payload_root.mkdir(parents=True, exist_ok=True)

    _write_synthetic_broken_package(target_root)
    _write_repair_payload(payload_root)

    broken = _run_synthetic_cli(target_root)
    assert broken.returncode != 0

    result = apply_bootstrap_repair(
        payload_root,
        target_root,
        ["demo_pkg/broken_mod.py"],
        py_compile_paths=["demo_pkg/broken_mod.py"],
    )

    assert result.ok is True
    assert result.restored_paths == ("demo_pkg/broken_mod.py",)
    assert result.write_records[0].existed_before is True
    assert result.write_records[0].backup_path is not None
    assert result.validation_records[0].exit_code == 0
    assert "bootstrap_repairs" in str(result.backup_root)

    repaired = _run_synthetic_cli(target_root)
    assert repaired.returncode == 0, repaired.stderr
    assert repaired.stdout.strip() == "repair-ok"


def test_bootstrap_repair_module_entrypoint_emits_json_and_recovers_file(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    payload_root = tmp_path / "payload"
    target_root.mkdir(parents=True, exist_ok=True)
    payload_root.mkdir(parents=True, exist_ok=True)

    _write_synthetic_broken_package(target_root)
    _write_repair_payload(payload_root)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.bootstrap_repair",
            str(payload_root),
            "--target-root",
            str(target_root),
            "--path",
            "demo_pkg/broken_mod.py",
            "--py-compile-path",
            "demo_pkg/broken_mod.py",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["target_root"] == str(target_root.resolve())
    assert payload["restored_paths"] == ["demo_pkg/broken_mod.py"]
    assert "Return to the normal PatchOps workflow" in payload["next_action"]

    repaired = _run_synthetic_cli(target_root)
    assert repaired.returncode == 0, repaired.stderr
    assert repaired.stdout.strip() == "repair-ok"


def test_bootstrap_repair_docs_mention_direct_module_and_cli_recovery_surfaces() -> None:
    quickstart = Path("docs/operator_quickstart.md").read_text(encoding="utf-8")
    repair_doc = Path("docs/bootstrap_repair.md").read_text(encoding="utf-8")

    assert "patchops.bootstrap_repair" in quickstart
    assert "patchops.cli bootstrap-repair" in quickstart
    assert "Return to the normal `check` / `inspect` / `plan` / `apply` / `verify`" in quickstart
    assert "not a second apply engine" in repair_doc
    assert "exceptional and narrow" in repair_doc
