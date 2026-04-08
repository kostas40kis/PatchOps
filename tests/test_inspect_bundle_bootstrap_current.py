from __future__ import annotations

import io
import json
import sys
import zipfile
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops import cli


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        try:
            exit_code = cli.main(argv)
        except SystemExit as exc:
            code = exc.code
            exit_code = int(code) if isinstance(code, int) else 0
    return int(exit_code), stdout_buffer.getvalue(), stderr_buffer.getvalue()


def _run_cli_json(argv: list[str]) -> tuple[int, dict]:
    exit_code, stdout_text, stderr_text = _run_cli(argv)
    text = stdout_text.strip()
    if not text:
        raise AssertionError(f"expected JSON output but stdout was empty; stderr={stderr_text!r}")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"stdout was not valid JSON: {stdout_text!r}; stderr={stderr_text!r}") from exc
    return exit_code, payload


def _write_valid_bundle(bundle_zip_path: Path) -> None:
    with zipfile.ZipFile(bundle_zip_path, "w") as zf:
        zf.writestr("patch_demo_bundle/manifest.json", "{}\n")
        zf.writestr("patch_demo_bundle/bundle_meta.json", "{}\n")
        zf.writestr("patch_demo_bundle/README.txt", "demo\n")
        zf.writestr("patch_demo_bundle/content/example.txt", "payload\n")
        zf.writestr("patch_demo_bundle/launchers/apply_with_patchops.ps1", "Write-Host demo\n")


def main() -> int:
    temp_root = PROJECT_ROOT / "data" / "runtime" / "inspect_bundle_bootstrap_temp"
    temp_root.mkdir(parents=True, exist_ok=True)

    help_exit, help_stdout, help_stderr = _run_cli(["inspect-bundle", "--help"])
    help_text = help_stdout + help_stderr
    if help_exit != 0:
        raise AssertionError(f"inspect-bundle --help exit_code={help_exit}")
    if "usage: patchops inspect-bundle" not in help_text:
        raise AssertionError(help_text)
    if "bundle_zip_path" not in help_text:
        raise AssertionError(help_text)

    valid_zip = temp_root / "demo_bundle.zip"
    _write_valid_bundle(valid_zip)
    exit_code, payload = _run_cli_json(["inspect-bundle", str(valid_zip)])
    if exit_code != 0:
        raise AssertionError(payload)
    assert payload["ok"] is True
    assert payload["exists"] is True
    assert payload["bundle_zip_path"] == str(valid_zip.resolve())
    assert payload["root_folder"] == "patch_demo_bundle"
    assert payload["manifest_path"] == "patch_demo_bundle/manifest.json"
    assert payload["bundle_meta_path"] == "patch_demo_bundle/bundle_meta.json"
    assert payload["readme_path"] == "patch_demo_bundle/README.txt"
    assert payload["content_prefix"] == "patch_demo_bundle/content/"
    assert payload["issue_count"] == 0
    assert payload["issues"] == []
    assert any(item.endswith("apply_with_patchops.ps1") for item in payload["launchers"])

    missing_manifest_zip = temp_root / "missing_manifest_bundle.zip"
    with zipfile.ZipFile(missing_manifest_zip, "w") as zf:
        zf.writestr("patch_demo_bundle/bundle_meta.json", "{}\n")
        zf.writestr("patch_demo_bundle/README.txt", "demo\n")
        zf.writestr("patch_demo_bundle/content/example.txt", "payload\n")
        zf.writestr("patch_demo_bundle/launchers/apply_with_patchops.ps1", "Write-Host demo\n")

    exit_code, payload = _run_cli_json(["inspect-bundle", str(missing_manifest_zip)])
    if exit_code != 1:
        raise AssertionError(payload)
    assert payload["ok"] is False
    assert payload["issue_count"] >= 1
    assert any("manifest.json" in issue for issue in payload["issues"])

    multi_root_zip = temp_root / "multi_root_bundle.zip"
    with zipfile.ZipFile(multi_root_zip, "w") as zf:
        zf.writestr("root_one/manifest.json", "{}\n")
        zf.writestr("root_two/bundle_meta.json", "{}\n")

    exit_code, payload = _run_cli_json(["inspect-bundle", str(multi_root_zip)])
    if exit_code != 1:
        raise AssertionError(payload)
    assert payload["ok"] is False
    assert payload["issue_count"] >= 1
    joined = "\n".join(payload["issues"]).lower()
    assert "top-level root" in joined or "exactly one" in joined

    print("inspect-bundle bootstrap validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
