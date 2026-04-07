from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import zipfile

from patchops.bundles import (
    native_zip_milestone_as_dict,
    prove_bundle_native_zip_milestone,
    prove_native_zip_milestone,
)


def _write_bundle_zip(bundle_zip_path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(bundle_zip_path, 'w') as archive:
        for relative_path, text in members.items():
            archive.writestr(relative_path, text)


def _bundle_meta(*, patch_name: str = 'patch_17_native_zip') -> str:
    return json.dumps(
        {
            'bundle_schema_version': 1,
            'patch_name': patch_name,
            'target_project': 'patchops',
            'recommended_profile': 'generic_python',
            'target_project_root': r'C:\dev\patchops',
            'wrapper_project_root': r'C:\dev\patchops',
            'content_root': 'content',
            'manifest_path': 'manifest.json',
            'launcher_path': 'run_with_patchops.ps1',
        }
    )


def _manifest(*, patch_name: str = 'patch_17_native_zip', content_path: str = 'content/docs/note.md') -> str:
    return json.dumps(
        {
            'manifest_version': '1',
            'patch_name': patch_name,
            'active_profile': 'generic_python',
            'target_project_root': r'C:\dev\patchops',
            'files_to_write': [
                {
                    'path': 'docs/note.md',
                    'content_path': content_path,
                    'encoding': 'utf-8',
                }
            ],
            'validation_commands': [],
        }
    )


def _fake_launcher_invocation(bundle_root: Path, wrapper_project_root: str | Path, *, mode: str = 'apply', powershell_program: str = 'powershell', env=None):
    return SimpleNamespace(
        resolution=SimpleNamespace(
            launcher_path=bundle_root / 'run_with_patchops.ps1',
            mode=mode,
            launcher_kind='root_single',
        ),
        cwd=bundle_root,
        command=(powershell_program, '-File', str(bundle_root / 'run_with_patchops.ps1')),
        exit_code=0,
        stdout='launcher ok',
        stderr='',
        report_path=bundle_root.parent / 'canonical_report.txt',
        inner_report_path=bundle_root.parent / 'inner_report.txt',
    )


def test_prove_native_zip_milestone_starts_from_raw_zip_and_invokes_launcher(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / 'patch_17_native_zip.zip'
    _write_bundle_zip(
        bundle_zip_path,
        {
            'manifest.json': _manifest(),
            'bundle_meta.json': _bundle_meta(),
            'run_with_patchops.ps1': r'& { py -m patchops.cli apply .\manifest.json }',
            'content/docs/note.md': 'demo note\n',
        },
    )
    wrapper_root = tmp_path / 'wrapper'
    wrapper_root.mkdir()

    result = prove_native_zip_milestone(
        bundle_zip_path,
        wrapper_root,
        timestamp_token='20260404_234500',
        launcher_invoke_func=_fake_launcher_invocation,
    )

    assert result.operator_can_skip_manual_unzip is True
    assert result.result_label == 'PASS'
    assert result.bundle_zip_path is not None and result.bundle_zip_path.endswith('patch_17_native_zip.zip')
    assert result.extracted_bundle_root is not None and result.extracted_bundle_root.endswith('extracted_bundle')
    assert result.launcher_path is not None and result.launcher_path.endswith('run_with_patchops.ps1')
    assert result.report_chain.final_report_path is not None and result.report_chain.final_report_path.endswith('canonical_report.txt')
    assert result.report_chain.inner_report_path is not None and result.report_chain.inner_report_path.endswith('inner_report.txt')
    assert Path(result.check.extraction.bundle_root).exists()


def test_native_zip_milestone_as_dict_exposes_skip_unzip_and_one_liner(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / 'patch_17_native_zip.zip'
    _write_bundle_zip(
        bundle_zip_path,
        {
            'manifest.json': _manifest(),
            'bundle_meta.json': _bundle_meta(),
            'run_with_patchops.ps1': r'& { py -m patchops.cli apply .\manifest.json }',
            'content/docs/note.md': 'demo note\n',
        },
    )
    wrapper_root = tmp_path / 'wrapper'
    wrapper_root.mkdir()

    payload = native_zip_milestone_as_dict(
        prove_bundle_native_zip_milestone(
            bundle_zip_path,
            wrapper_root,
            timestamp_token='20260404_234501',
            launcher_invoke_func=_fake_launcher_invocation,
        )
    )

    assert payload['operator_can_skip_manual_unzip'] is True
    assert payload['launcher_exit_code'] == 0
    assert payload['result_label'] == 'PASS'
    assert 'apply-bundle' in payload['operator_one_liner']
    assert 'raw zip' in payload['proof_summary'].lower()


def test_prove_native_zip_milestone_supports_verify_mode(tmp_path: Path) -> None:
    bundle_zip_path = tmp_path / 'patch_17_verify.zip'
    _write_bundle_zip(
        bundle_zip_path,
        {
            'manifest.json': _manifest(patch_name='patch_17_verify'),
            'bundle_meta.json': _bundle_meta(patch_name='patch_17_verify'),
            'run_with_patchops.ps1': r'& { py -m patchops.cli verify .\manifest.json }',
            'content/docs/note.md': 'demo note\n',
        },
    )
    wrapper_root = tmp_path / 'wrapper'
    wrapper_root.mkdir()

    result = prove_native_zip_milestone(
        bundle_zip_path,
        wrapper_root,
        mode='verify',
        timestamp_token='20260404_234502',
        launcher_invoke_func=_fake_launcher_invocation,
    )

    assert result.mode == 'verify'
    assert result.report_chain.launcher_mode == 'verify'
    assert 'verify-bundle' in result.operator_one_liner
