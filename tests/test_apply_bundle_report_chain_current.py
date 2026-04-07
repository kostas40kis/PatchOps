from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from patchops import cli
from patchops.bundles import bundle_zip_apply


@pytest.fixture()
def simple_bundle_zip(tmp_path: Path) -> Path:
    bundle_root = 'demo_bundle'
    zip_path = tmp_path / 'demo_bundle.zip'
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr(f"{bundle_root}/manifest.json", "{}\n")
        zf.writestr(f"{bundle_root}/bundle_meta.json", "{}\n")
        zf.writestr(f"{bundle_root}/README.txt", "demo\n")
        zf.writestr(f"{bundle_root}/content/marker.txt", "hello\n")
        zf.writestr(
            f"{bundle_root}/launchers/apply_with_patchops.ps1",
            "& {\nparam([string]$WrapperRepoRoot)\nWrite-Host 'apply bundle launcher'\n}\n",
        )
    return zip_path


def test_apply_bundle_report_chain_extracts_summary_fields(
    simple_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(command: list[str], working_directory: Path):
        class Result:
            returncode = 0
            stdout = (
                'PATCHOPS RUN SUMMARY\n'
                '--------------------\n'
                'Mode               : apply\n'
                'Patch Name         : demo\n'
                'Wrapper Project Root : C:/dev/patchops\n'
                'Target Project Root: C:/dev/patchops\n'
                'Active Profile     : generic_python\n'
                'Manifest Path Used : C:/demo/manifest.json\n'
                'Report Path        : C:/Users/kostas/Desktop/demo_report.txt\n'
                'ExitCode           : 0\n'
                'Result             : PASS\n'
            )
            stderr = ''
        return Result()

    monkeypatch.setattr(bundle_zip_apply, '_run_launcher_command', fake_run)
    exit_code = cli.main([
        'apply-bundle',
        str(simple_bundle_zip),
        '--wrapper-root',
        'C:/dev/patchops',
        '--extract-root',
        str(tmp_path / 'bundle_run'),
    ])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    chain = payload['report_chain']
    assert payload['final_report_path'] == 'C:/Users/kostas/Desktop/demo_report.txt'
    assert payload['related_inner_report_path'] == 'C:/Users/kostas/Desktop/demo_report.txt'
    assert chain['target_project_root'] == 'C:/dev/patchops'
    assert chain['active_profile'] == 'generic_python'
    assert chain['manifest_path_reported'] == 'C:/demo/manifest.json'
    assert chain['wrapper_project_root_reported'] == 'C:/dev/patchops'


def test_apply_bundle_report_chain_handles_missing_summary_lines(
    simple_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(command: list[str], working_directory: Path):
        class Result:
            returncode = 0
            stdout = 'launcher ok\n'
            stderr = ''
        return Result()

    monkeypatch.setattr(bundle_zip_apply, '_run_launcher_command', fake_run)
    exit_code = cli.main([
        'apply-bundle',
        str(simple_bundle_zip),
        '--extract-root',
        str(tmp_path / 'bundle_run_no_summary'),
    ])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    chain = payload['report_chain']
    assert payload['final_report_path'] is None
    assert chain['related_inner_report_path'] is None
    assert chain['target_project_root'] is None
    assert chain['active_profile'] is None


def test_apply_bundle_report_chain_preserves_paths_and_presence_flags(
    simple_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(command: list[str], working_directory: Path):
        class Result:
            returncode = 0
            stdout = 'launcher ok\n'
            stderr = 'warning\n'
        return Result()

    monkeypatch.setattr(bundle_zip_apply, '_run_launcher_command', fake_run)
    exit_code = cli.main([
        'apply-bundle',
        str(simple_bundle_zip),
        '--extract-root',
        str(tmp_path / 'bundle_run_flags'),
    ])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    chain = payload['report_chain']
    assert chain['zip_path'] == str(simple_bundle_zip.resolve())
    assert chain['bundle_root'].endswith('demo_bundle')
    assert chain['launcher_path'].endswith('apply_with_patchops.ps1')
    assert chain['launcher_stdout_present'] is True
    assert chain['launcher_stderr_present'] is True


def test_apply_bundle_report_chain_nonzero_exit_still_preserves_chain(
    simple_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(command: list[str], working_directory: Path):
        class Result:
            returncode = 7
            stdout = 'Report Path        : C:/Users/kostas/Desktop/fail_report.txt\n'
            stderr = 'launcher failed\n'
        return Result()

    monkeypatch.setattr(bundle_zip_apply, '_run_launcher_command', fake_run)
    exit_code = cli.main([
        'apply-bundle',
        str(simple_bundle_zip),
        '--extract-root',
        str(tmp_path / 'bundle_run_fail_chain'),
    ])
    assert exit_code == 7
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is False
    assert payload['final_report_path'] == 'C:/Users/kostas/Desktop/fail_report.txt'
    assert payload['report_chain']['related_inner_report_path'] == 'C:/Users/kostas/Desktop/fail_report.txt'
