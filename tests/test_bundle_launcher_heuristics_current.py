from __future__ import annotations

from patchops.bundles.launcher_builder import build_patchops_bundle_launcher
from patchops.bundles.launcher_heuristics import (
    audit_bundle_launcher_text,
    find_common_launcher_mistakes,
)


def _codes(text: str) -> tuple[str, ...]:
    return tuple(item.code for item in find_common_launcher_mistakes(text))


def test_clean_builder_output_has_no_risk_findings() -> None:
    launcher = build_patchops_bundle_launcher(mode="apply")
    report = audit_bundle_launcher_text(launcher)
    assert report.ok is True
    assert report.warning_count == 0
    assert report.codes == ()


def test_detects_fragile_json_handoff() -> None:
    text = '''
    $state = Get-Content $prepPath | ConvertFrom-Json
    '''
    assert "fragile_json_handoff" in _codes(text)


def test_detects_inline_python_and_here_string_usage() -> None:
    text = '''
    $py = @"
    print("hello")
    "@
    py -c $py
    '''
    codes = _codes(text)
    assert "large_inline_python_emission" in codes
    assert "suspicious_here_string_usage" in codes
    assert "missing_standard_invocation_block" in codes


def test_detects_manual_copy_logic_and_direct_unittest_main_path() -> None:
    text = '''
    Copy-Item $bundleFile $targetFile -Force
    py -m unittest tests.test_example
    '''
    codes = _codes(text)
    assert "manual_copy_logic_main_path" in codes
    assert "direct_unittest_main_path" in codes
    assert "missing_standard_invocation_block" in codes


def test_detects_unsafe_report_buffer_patterns() -> None:
    text = '''
    $reportLines.Add("hello")
    Add-SectionHeader -Lines $reportLines -Title 'ERROR'
    Write-ReportFile -Path $path -Lines $reportLines
    '''
    assert "unsafe_report_buffer_patterns" in _codes(text)


def test_detects_brittle_exact_text_surgery() -> None:
    text = '''
    $body = Get-Content $path -Raw
    $body = $body.Replace("old", "new")
    [System.IO.File]::WriteAllText($path, $body)
    '''
    assert "brittle_exact_text_surgery" in _codes(text)


def test_detects_suspicious_nested_quoting_backslash_shapes() -> None:
    text = '''
    $code = @"
    path = path.replace("\\", "/")
    "@
    py -c $code
    '''
    assert "suspicious_nested_quoting_backslash_shape" in _codes(text)
