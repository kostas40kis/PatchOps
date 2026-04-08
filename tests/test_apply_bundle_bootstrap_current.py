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

from patchops import cli


def _capture_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        exit_code = cli.main(argv)
    return int(exit_code), stdout_buffer.getvalue(), stderr_buffer.getvalue()


def _write_demo_bundle(bundle_zip_path: Path, wrapper_root: Path) -> Path:
    work_root = bundle_zip_path.parent
    bundle_root_name = 'patch_demo_bundle'
    bundle_root = work_root / bundle_root_name
    content_root = bundle_root / 'content'
    launchers_root = bundle_root / 'launchers'
    content_root.mkdir(parents=True, exist_ok=True)
    launchers_root.mkdir(parents=True, exist_ok=True)

    target_root = work_root / 'target_root'
    target_root.mkdir(parents=True, exist_ok=True)
    target_root_str = target_root.as_posix()

    manifest = {
        'manifest_version': '1',
        'patch_name': 'patch_demo_bundle',
        'active_profile': 'generic_python',
        'target_project_root': target_root_str,
        'files_to_write': [
            {
                'path': 'marker.txt',
                'content_path': 'content/marker.txt',
                'encoding': 'utf-8',
            }
        ],
        'validation_commands': [],
        'report_preferences': {
            'write_to_desktop': False,
            'report_name_prefix': 'patch_demo_bundle',
        },
    }
    (bundle_root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    (bundle_root / 'bundle_meta.json').write_text(json.dumps({
        'schema_version': '1',
        'patch_name': 'patch_demo_bundle',
        'manifest_path': 'manifest.json',
        'launcher_paths': ['launchers/apply_with_patchops.ps1'],
        'content_root': 'content',
    }, indent=2) + '\n', encoding='utf-8')
    (bundle_root / 'README.txt').write_text('demo\n', encoding='utf-8')
    (content_root / 'marker.txt').write_text('hello from apply-bundle demo\n', encoding='utf-8')
    launcher_text = (
        "param([string]$WrapperRepoRoot)\n"
        "$ErrorActionPreference = 'Stop'\n"
        "if (-not $WrapperRepoRoot) { throw 'WrapperRepoRoot was not provided.' }\n"
        "$launcherDir = Split-Path -Parent $PSCommandPath\n"
        "$bundleRoot = Split-Path -Parent $launcherDir\n"
        "$manifestPath = Join-Path $bundleRoot 'manifest.json'\n"
        "Push-Location $WrapperRepoRoot\n"
        "try {\n"
        "    py -m patchops.cli apply $manifestPath --wrapper-root $WrapperRepoRoot\n"
        "}\n"
        "finally {\n"
        "    Pop-Location\n"
        "}\n"
    )
    (launchers_root / 'apply_with_patchops.ps1').write_text(launcher_text, encoding='utf-8')

    with zipfile.ZipFile(bundle_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in bundle_root.rglob('*'):
            if path.is_file():
                zf.write(path, arcname=f'{bundle_root_name}/{path.relative_to(bundle_root).as_posix()}')
    return target_root


def main() -> int:
    wrapper_root = PROJECT_ROOT
    with tempfile.TemporaryDirectory(prefix='apply_bundle_bootstrap_') as tmp:
        tmp_path = Path(tmp)
        bundle_zip_path = tmp_path / 'patch_demo_bundle.zip'
        target_root = _write_demo_bundle(bundle_zip_path, wrapper_root)
        exit_code, stdout_text, stderr_text = _capture_cli([
            'apply-bundle',
            str(bundle_zip_path),
            '--wrapper-root',
            str(wrapper_root),
        ])
        if not stdout_text.strip():
            raise AssertionError('No CLI stdout captured. stderr was:\n' + stderr_text)
        payload = json.loads(stdout_text)
        if exit_code != 0:
            raise AssertionError(
                'apply-bundle returned nonzero exit code: '
                + str(exit_code)
                + '\npayload:\n'
                + json.dumps(payload, indent=2, sort_keys=True)
                + '\nstderr:\n'
                + stderr_text
            )
        assert payload['ok'] is True
        assert int(payload['exit_code']) == 0
        assert payload['launcher_path'].endswith('apply_with_patchops.ps1')
        assert payload['manifest_path'].endswith('manifest.json')
        assert payload['command'][0].lower().startswith('powershell')
        marker_path = target_root / 'marker.txt'
        assert marker_path.exists(), f'Marker file missing: {marker_path}'
        assert marker_path.read_text(encoding='utf-8') == 'hello from apply-bundle demo\n'
        print('apply-bundle bootstrap validation PASS')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
