from __future__ import annotations

import io
import json
import sys
import tempfile
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops import cli  # noqa: E402


def _run_cli(argv: list[str]) -> tuple[int, dict[str, object], str]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        exit_code = cli.main(argv)
    stdout_text = stdout_buffer.getvalue().strip()
    stderr_text = stderr_buffer.getvalue().strip()
    if not stdout_text:
        raise AssertionError("No CLI stdout captured. stderr was:\n" + stderr_text)
    payload = json.loads(stdout_text)
    return int(exit_code), payload, stderr_text


def _write_single_root_demo_zip(zip_path: Path, target_root: Path) -> None:
    bundle_root_name = "patch_demo_bundle"
    target_root_text = str(target_root).replace("\\", "/")
    wrapper_root_text = str(PROJECT_ROOT).replace("\\", "/")

    manifest = {
        "manifest_version": "1",
        "patch_name": bundle_root_name,
        "active_profile": "generic_python",
        "target_project_root": target_root_text,
        "backup_files": ["marker.txt"],
        "files_to_write": [
            {
                "path": "marker.txt",
                "content": None,
                "content_path": "content/marker.txt",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": None,
            "report_name_prefix": bundle_root_name,
            "write_to_desktop": True,
        },
        "tags": ["demo", "bundle", "verify-bundle"],
        "notes": "Single-root demo bundle for verify-bundle bootstrap validation.",
    }
    bundle_meta = {
        "schema_version": "1",
        "bundle_schema_version": 1,
        "patch_name": bundle_root_name,
        "target_project": "demo",
        "recommended_profile": "generic_python",
        "target_project_root": target_root_text,
        "wrapper_project_root": wrapper_root_text,
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
        "launcher_paths": ["run_with_patchops.ps1"],
        "bundle_mode": "verify",
    }
    root_launcher = "param([string]$WrapperRepoRoot)\nWrite-Host verify-demo\n"

    members: dict[str, str] = {
        f"{bundle_root_name}/manifest.json": json.dumps(manifest, indent=2) + "\n",
        f"{bundle_root_name}/bundle_meta.json": json.dumps(bundle_meta, indent=2) + "\n",
        f"{bundle_root_name}/README.txt": "verify demo bundle\n",
        f"{bundle_root_name}/run_with_patchops.ps1": root_launcher,
        f"{bundle_root_name}/content/marker.txt": "demo\n",
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in members.items():
            zf.writestr(name, content)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="verify_bundle_bootstrap_") as temp_dir:
        temp_root = Path(temp_dir)
        target_root = temp_root / "target_root"
        target_root.mkdir(parents=True, exist_ok=True)
        marker_path = target_root / "marker.txt"
        marker_path.write_text("demo\n", encoding="utf-8")

        bundle_zip_path = temp_root / "patch_demo_bundle.zip"
        _write_single_root_demo_zip(bundle_zip_path, target_root)

        exit_code, payload, stderr = _run_cli(
            ["verify-bundle", str(bundle_zip_path), "--wrapper-root", str(PROJECT_ROOT)]
        )
        payload_json = json.dumps(payload, indent=2, sort_keys=True)

        if exit_code != 0:
            raise AssertionError(
                "verify-bundle returned nonzero exit code: "
                + str(exit_code)
                + "\npayload:\n"
                + payload_json
                + "\nstderr:\n"
                + stderr
            )

        if payload.get("patch_name") != "patch_demo_bundle":
            raise AssertionError("Unexpected patch_name in payload:\n" + payload_json)

        prepared_manifest_path = payload.get("prepared_manifest_path")
        if not prepared_manifest_path:
            raise AssertionError("prepared_manifest_path was not populated:\n" + payload_json)

        report_chain = payload.get("report_chain") or {}
        report_path = payload.get("report_path") or report_chain.get("final_report_path")
        if not report_path:
            raise AssertionError("verify-bundle did not return a report path:\n" + payload_json)

        report_text = Path(str(report_path)).read_text(encoding="utf-8")
        if "PATCHOPS VERIFY_ONLY" not in report_text:
            raise AssertionError("verify report did not contain PATCHOPS VERIFY_ONLY header")

        if marker_path.read_text(encoding="utf-8") != "demo\n":
            raise AssertionError("verify-bundle changed the target file unexpectedly.")

    print("verify-bundle bootstrap validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
