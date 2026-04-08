from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops import cli


def _run_cli(argv: list[str]) -> tuple[int, dict]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
        exit_code = cli.main(argv)
    stdout_text = stdout_buffer.getvalue().strip()
    if not stdout_text:
        raise AssertionError(f"No CLI stdout captured. stderr was:\n{stderr_buffer.getvalue()}")
    return int(exit_code), json.loads(stdout_text)


def _write_valid_bundle_zip(bundle_zip_path: Path) -> None:
    with zipfile.ZipFile(bundle_zip_path, "w") as zf:
        zf.writestr("patch_demo_bundle/manifest.json", "{}\n")
        zf.writestr(
            "patch_demo_bundle/bundle_meta.json",
            json.dumps(
                {
                    "schema_version": "1",
                    "patch_name": "patch_demo_bundle",
                    "target_project": "patchops",
                    "recommended_profile": "generic_python",
                    "content_root": "content",
                    "manifest_path": "manifest.json",
                    "launcher_paths": {"apply": "launchers/apply_with_patchops.ps1"},
                    "bundle_mode": "apply",
                },
                indent=2,
            )
            + "\n",
        )
        zf.writestr("patch_demo_bundle/README.txt", "demo\n")
        zf.writestr("patch_demo_bundle/content/example.txt", "payload\n")
        zf.writestr("patch_demo_bundle/launchers/apply_with_patchops.ps1", "Write-Host demo\n")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)

        valid_zip = tmp_path / "patch_demo_bundle.zip"
        _write_valid_bundle_zip(valid_zip)

        exit_code, payload = _run_cli(["plan-bundle", str(valid_zip)])
        assert exit_code == 0
        assert payload["ok"] is True
        assert payload["issue_count"] == 0
        assert payload["issues"] == []
        command_plan = payload.get("command_plan")
        assert isinstance(command_plan, list)
        assert any("check-bundle" in item for item in command_plan)
        assert any("inspect-bundle" in item for item in command_plan)
        assert any("plan-bundle" in item for item in command_plan)

        missing_meta_zip = tmp_path / "missing_bundle_meta_bundle.zip"
        with zipfile.ZipFile(missing_meta_zip, "w") as zf:
            zf.writestr("patch_demo_bundle/manifest.json", "{}\n")
            zf.writestr("patch_demo_bundle/README.txt", "demo\n")
            zf.writestr("patch_demo_bundle/content/example.txt", "payload\n")
            zf.writestr("patch_demo_bundle/launchers/apply_with_patchops.ps1", "Write-Host demo\n")

        exit_code, payload = _run_cli(["plan-bundle", str(missing_meta_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert payload["issue_count"] >= 1
        assert any("bundle_meta.json" in issue for issue in payload["issues"])

        multi_root_zip = tmp_path / "multi_root_bundle.zip"
        with zipfile.ZipFile(multi_root_zip, "w") as zf:
            zf.writestr("root_one/manifest.json", "{}\n")
            zf.writestr("root_two/bundle_meta.json", "{}\n")

        exit_code, payload = _run_cli(["plan-bundle", str(multi_root_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert payload["issue_count"] >= 1
        joined = "\n".join(payload["issues"]).lower()
        assert "top-level root" in joined or "exactly one" in joined

    print("plan-bundle bootstrap validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
