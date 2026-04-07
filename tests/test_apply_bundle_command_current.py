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


def test_apply_bundle_help_exposes_current_live_args(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(['apply-bundle', '--help'])
    assert exc.value.code == 0
    text = capsys.readouterr().out + capsys.readouterr().err
    assert 'usage: patchops apply-bundle' in text
    assert 'bundle_zip_path' in text


def test_apply_bundle_returns_success_payload_when_launcher_runner_succeeds(
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
        '--wrapper-root',
        'C:/dev/patchops',
        '--extract-root',
        str(tmp_path / 'bundle_run'),
    ])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is True
    assert payload['exit_code'] == 0
    assert payload['launcher_path'].endswith('apply_with_patchops.ps1')
    assert payload['manifest_path'].endswith('manifest.json')
    assert payload['command'][0].lower().startswith('powershell')


def test_apply_bundle_returns_nonzero_payload_when_launcher_runner_fails(
    simple_bundle_zip: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(command: list[str], working_directory: Path):
        class Result:
            returncode = 5
            stdout = ''
            stderr = 'launcher failed\n'
        return Result()

    monkeypatch.setattr(bundle_zip_apply, '_run_launcher_command', fake_run)
    exit_code = cli.main([
        'apply-bundle',
        str(simple_bundle_zip),
        '--extract-root',
        str(tmp_path / 'bundle_run_fail'),
    ])
    assert exit_code == 5
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is False
    assert payload['exit_code'] == 5
    assert 'launcher failed' in payload['stderr']


def test_apply_bundle_returns_nonzero_for_missing_zip(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    missing = tmp_path / 'missing_bundle.zip'
    exit_code = cli.main(['apply-bundle', str(missing)])
    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload['ok'] is False
    assert 'does not exist' in payload['error'].lower()
