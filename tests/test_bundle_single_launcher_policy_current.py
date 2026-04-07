from __future__ import annotations

from pathlib import Path

from patchops.bundles.launcher_builder import (
    build_patchops_bundle_launcher,
    ensure_powershell_block_wrapped,
)


def test_single_launcher_docs_lock_manual_unzip_and_one_report_rule() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    standard_text = (repo_root / 'docs' / 'zip_bundle_standard.md').read_text(encoding='utf-8').lower()
    template_text = (repo_root / 'docs' / 'bundle_authoring_template.md').read_text(encoding='utf-8').lower()

    required_standard = [
        'run_with_patchops.ps1',
        'one patch zip',
        'manual unzip is still expected',
        'one canonical desktop txt report',
        'one root-level launcher is enough',
        'bundle root contents directly',
        'redundant second parent folder inside the zip',
    ]
    missing_standard = [phrase for phrase in required_standard if phrase not in standard_text]
    assert not missing_standard, f'standard doc is missing required phrases: {missing_standard}'

    required_template = [
        'one folder is enough',
        'one root-level powershell file is enough',
        'one canonical desktop txt report is enough',
        'run_with_patchops.ps1',
        'archive the bundle root contents directly',
    ]
    missing_template = [phrase for phrase in required_template if phrase not in template_text]
    assert not missing_template, f'template doc is missing required phrases: {missing_template}'


def test_launcher_builder_emits_wrapped_root_launcher_with_apply_path() -> None:
    launcher_text = build_patchops_bundle_launcher()

    assert launcher_text.startswith('& {')
    assert 'Set-StrictMode -Version Latest' in launcher_text
    assert '[string]$WrapperRepoRoot' in launcher_text
    assert 'WrapperProjectRoot' not in launcher_text
    assert "$bundleRoot = $PSScriptRoot" in launcher_text
    assert "Join-Path $bundleRoot 'manifest.json'" in launcher_text
    assert 'Push-Location -LiteralPath $WrapperRepoRoot' in launcher_text
    assert 'py -m patchops.cli check $manifestPath' in launcher_text
    assert 'py -m patchops.cli inspect $manifestPath' in launcher_text
    assert 'py -m patchops.cli plan $manifestPath' in launcher_text
    assert 'py -m patchops.cli apply $manifestPath' in launcher_text
    assert 'py -m patchops.cli verify $manifestPath' not in launcher_text
    assert 'ProcessStartInfo.ArgumentList' not in launcher_text


def test_launcher_builder_supports_verify_mode_without_adding_apply_path() -> None:
    launcher_text = build_patchops_bundle_launcher(mode='verify')

    assert launcher_text.startswith('& {')
    assert '[string]$WrapperRepoRoot' in launcher_text
    assert 'py -m patchops.cli check $manifestPath' in launcher_text
    assert 'py -m patchops.cli verify $manifestPath' in launcher_text
    assert 'py -m patchops.cli apply $manifestPath' not in launcher_text


def test_wrapper_helper_adds_ampersand_block_only_when_missing() -> None:
    wrapped = ensure_powershell_block_wrapped("Write-Host 'hello'")
    already = ensure_powershell_block_wrapped("& {\n    Write-Host 'hello'\n}\n")

    assert wrapped.startswith('& {')
    assert wrapped.rstrip().endswith('}')
    assert already.startswith('& {')
    assert already.count('& {') == 1
