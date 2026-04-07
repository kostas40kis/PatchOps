from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from patchops import cli
from patchops.bundles import bundle_zip_apply


@pytest.fixture()
def milestone_bundle_zip(tmp_path: Path) -> Path:
    bundle_root = "milestone_bundle"
    zip_path = tmp_path / "milestone_bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(f"{bundle_root}/manifest.json", "{}\n")
        zf.writestr(f"{bundle_root}/bundle_meta.json", "{}\n")
        zf.writestr(f"{bundle_root}/README.txt", "demo\n")
        zf.writestr(f"{bundle_root}/content/marker.txt", "hello\n")
        zf.writestr(
            f"{bundle_root}/launchers/apply_with_patchops.ps1",
            "& {\n"
            "param([string]$WrapperRepoRoot)\n"
            "Write-Host 'apply bundle launcher'\n"
            "}\n",
        )
    return zip_path


def test_native_zip_milestone_proof_runs_from_zip_only(
    milestone_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured: dict[str, object] = {}
    extract_root = tmp_path / "bundle_run"

    def fake_run(command: list[str], working_directory: Path):
        captured["command"] = command
        captured["working_directory"] = working_directory

        class Result:
            returncode = 0
            stdout = (
                "PATCHOPS RUN SUMMARY\n"
                "--------------------\n"
                "Mode               : apply\n"
                "Patch Name         : milestone_demo\n"
                "Wrapper Project Root : C:/dev/patchops\n"
                "Target Project Root: C:/dev/patchops\n"
                "Active Profile     : generic_python\n"
                "Manifest Path Used : C:/demo/manifest.json\n"
                "Report Path        : C:/Users/kostas/Desktop/milestone_report.txt\n"
                "ExitCode           : 0\n"
                "Result             : PASS\n"
            )
            stderr = ""

        return Result()

    monkeypatch.setattr(bundle_zip_apply, "_run_launcher_command", fake_run)

    assert not extract_root.exists()
    exit_code = cli.main(
        [
            "apply-bundle",
            str(milestone_bundle_zip),
            "--wrapper-root",
            "C:/dev/patchops",
            "--extract-root",
            str(extract_root),
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["zip_path"] == str(milestone_bundle_zip.resolve())
    assert Path(payload["extract_root"]).exists()
    assert Path(payload["bundle_root"]).exists()
    assert Path(payload["manifest_path"]).exists()
    assert payload["launcher_path"].endswith("apply_with_patchops.ps1")
    assert payload["final_report_path"] == "C:/Users/kostas/Desktop/milestone_report.txt"
    assert payload["related_inner_report_path"] == "C:/Users/kostas/Desktop/milestone_report.txt"

    chain = payload["report_chain"]
    assert chain["zip_path"] == str(milestone_bundle_zip.resolve())
    assert chain["launcher_path"].endswith("apply_with_patchops.ps1")
    assert chain["manifest_path_reported"] == "C:/demo/manifest.json"
    assert chain["wrapper_project_root_reported"] == "C:/dev/patchops"
    assert chain["target_project_root"] == "C:/dev/patchops"
    assert chain["active_profile"] == "generic_python"
    assert chain["related_inner_report_path"] == "C:/Users/kostas/Desktop/milestone_report.txt"

    command = captured["command"]
    assert isinstance(command, list)
    assert command[0].lower().endswith("powershell")
    assert any(str(part).endswith("apply_with_patchops.ps1") for part in command)

    working_directory = captured["working_directory"]
    assert isinstance(working_directory, Path)
    assert working_directory == Path(payload["bundle_root"])


def test_native_zip_milestone_proof_preserves_non_bundle_regressions_through_validation_stack(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["check-launcher", "--help"])
    assert exc.value.code == 0
    text = capsys.readouterr().out
    assert "usage: patchops check-launcher" in text