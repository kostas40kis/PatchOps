from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops import cli
from patchops.bundle_review import check_bundle_cli_payload, check_bundle_payload


def _write_zip(bundle_path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(bundle_path, "w") as zf:
        for member_name, content in members.items():
            zf.writestr(member_name, content)


def _issue_codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["issues"]}


def _warning_codes(payload: dict) -> set[str]:
    return {item["code"] for item in payload["warnings"]}


def _run_cli(argv: list[str]) -> tuple[int, dict]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exit_code = cli.main(argv)
    payload = json.loads(buffer.getvalue())
    return exit_code, payload


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)

        valid_zip = tmp_path / "valid_bundle.zip"
        _write_zip(
            valid_zip,
            {
                "sample_bundle/manifest.json": "{}\n",
                "sample_bundle/run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }\n",
                "sample_bundle/content/example.txt": "demo\n",
            },
        )
        payload = check_bundle_payload(valid_zip, profile_name="generic_python")
        assert payload["ok"] is True
        assert payload["issue_count"] == 0
        assert payload["top_level_root"] == "sample_bundle"
        assert payload["profile"] == "generic_python"
        assert "missing_bundle_meta" in _warning_codes(payload)

        exit_code, cli_payload = _run_cli(["check-bundle", str(valid_zip)])
        assert exit_code == 0
        assert cli_payload["ok"] is True
        assert cli_payload["issue_count"] == 0
        assert cli_payload["top_level_root"] == "sample_bundle"
        assert "missing_bundle_meta" in _warning_codes(cli_payload)

        missing_manifest_zip = tmp_path / "missing_manifest_bundle.zip"
        _write_zip(
            missing_manifest_zip,
            {
                "sample_bundle/run_with_patchops.ps1": "& { py -m patchops.cli apply .\\manifest.json }\n",
                "sample_bundle/content/example.txt": "demo\n",
            },
        )
        exit_code, payload = _run_cli(["check-bundle", str(missing_manifest_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert "missing_manifest" in _issue_codes(payload)

        multiple_roots_zip = tmp_path / "multiple_roots_bundle.zip"
        _write_zip(
            multiple_roots_zip,
            {
                "root_one/manifest.json": "{}\n",
                "root_two/manifest.json": "{}\n",
            },
        )
        exit_code, payload = _run_cli(["check-bundle", str(multiple_roots_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert payload["top_level_root"] is None
        assert "multiple_roots" in _issue_codes(payload)

        missing_zip = tmp_path / "missing_bundle.zip"
        exit_code, payload = _run_cli(["check-bundle", str(missing_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert payload["exists"] is False
        assert "missing_bundle_zip" in _issue_codes(payload)

        invalid_zip = tmp_path / "invalid_bundle.zip"
        invalid_zip.write_text("not a real zip\n", encoding="utf-8")
        exit_code, payload = _run_cli(["check-bundle", str(invalid_zip)])
        assert exit_code == 1
        assert payload["ok"] is False
        assert "invalid_zip" in _issue_codes(payload)

        class Namespace:
            bundle_zip_path = str(valid_zip)
            wrapper_root = str(tmp_path)
            profile = "generic_python"
            timestamp_token = "20260408_000000"

        payload = check_bundle_cli_payload(Namespace())
        assert payload["path"] == str(valid_zip.resolve())
        assert payload["profile"] == "generic_python"

        payload = check_bundle_cli_payload(
            bundle_zip_path=str(valid_zip),
            wrapper_project_root=str(tmp_path),
            profile_name="generic_python",
            timestamp_token="20260408_000000",
        )
        assert payload["path"] == str(valid_zip.resolve())
        assert payload["profile"] == "generic_python"

    print("check-bundle bootstrap validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
