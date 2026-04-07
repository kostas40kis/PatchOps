from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.models import CommandResult
from patchops.reporting import (
    ReportHeaderMetadata,
    RunOriginMetadata,
    render_report_header,
    render_report_header_lines,
)
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    ReportCommandSection,
    render_report_command_output_section,
)
from patchops.reporting import renderer as report_renderer


def _command_result(name: str, stdout: str, stderr: str) -> CommandResult:
    return CommandResult(
        name='beta' if name == 'beta' else name,
        program='py',
        args=['-m', 'pytest', '-q'],
        working_directory=Path('C:/dev/patchops'),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command='py -m pytest -q',
        phase='validation',
    )


def test_reporting_public_exports_remain_available() -> None:
    from patchops import reporting

    exported = set(reporting.__all__)
    assert 'ReportHeaderMetadata' in exported
    assert 'RunOriginMetadata' in exported
    assert 'build_report_header_metadata' in exported
    assert 'build_run_origin_metadata' in exported
    assert 'render_report_header' in exported
    assert 'render_report_header_lines' in exported


def test_render_report_header_lines_include_run_origin_fields() -> None:
    manifest_path = Path('C:/bundle/manifest.json')
    metadata = ReportHeaderMetadata(
        patch_name='zp11a_reporting_model_path_contract_alignment_repair',
        timestamp='2026-04-07 15:31:05',
        workspace_root=Path('C:/dev'),
        wrapper_project_root=Path('C:/dev/patchops'),
        target_project_root=Path('C:/dev/patchops'),
        active_profile='generic_python',
        runtime_path=None,
        report_path=Path('C:/Users/kostas/Desktop/report.txt'),
        manifest_path=manifest_path,
        mode='apply',
        backup_root=Path('C:/dev/patchops/data/runtime/patch_backups/zp11a'),
        manifest_version='1',
        run_origin=RunOriginMetadata(
            workflow_mode='apply',
            manifest_path=manifest_path,
            active_profile='generic_python',
            resolved_runtime=None,
            wrapper_project_root=Path('C:/dev/patchops'),
            target_project_root=Path('C:/dev/patchops'),
            file_write_origin='wrapper_owned_write_engine',
        ),
    )

    lines = render_report_header_lines(metadata)
    text = '\n'.join(lines)
    manifest_text = str(manifest_path)

    assert lines[0] == 'PATCHOPS APPLY'
    assert 'Patch Name           : zp11a_reporting_model_path_contract_alignment_repair' in text
    assert 'Wrapper Mode Used    : apply' in text
    assert 'Manifest Path Used   :' in text
    assert manifest_text in text
    assert 'File Write Origin    : wrapper_owned_write_engine' in text
    assert 'Manifest Version     : 1' in text


def test_render_report_header_accepts_metadata_directly() -> None:
    manifest_path = Path('C:/bundle/manifest.json')
    metadata = ReportHeaderMetadata(
        patch_name='zp11a_reporting_model_path_contract_alignment_repair',
        manifest_path=manifest_path,
        mode='verify',
    )

    text = render_report_header(metadata)

    assert text.startswith('PATCHOPS VERIFY')
    assert 'Patch Name           : zp11a_reporting_model_path_contract_alignment_repair' in text
    assert f'Manifest Path        : {manifest_path}' in text


def test_report_command_output_section_renders_multi_result_output() -> None:
    section = ReportCommandOutputSection(
        title='FULL OUTPUT',
        results=[
            ReportCommandSection(
                section_label='FULL OUTPUT',
                command_name='alpha',
                command_text='py -m pytest -q tests/test_alpha.py',
                working_directory='C:/dev/patchops',
                exit_code=0,
                stdout='alpha stdout',
                stderr='alpha stderr',
            ),
            _command_result('beta', 'beta stdout', 'beta stderr'),
        ],
        rule=lambda title: f'\n{title}\n' + '-' * len(title),
    )

    text = render_report_command_output_section(section)

    assert text.lstrip().startswith('FULL OUTPUT')
    assert '[alpha][stdout]' in text
    assert '[alpha][stderr]' in text
    assert '[beta][stdout]' in text
    assert '[beta][stderr]' in text
    assert 'alpha stdout' in text
    assert 'beta stderr' in text


def test_render_workflow_report_composes_sections_from_current_python_surfaces(monkeypatch) -> None:
    monkeypatch.setattr(
        report_renderer,
        'derive_effective_summary_fields',
        lambda result: {'exit_code': 0, 'result_label': 'PASS'},
    )
    monkeypatch.setattr(report_renderer, 'header_section', lambda result: 'HEADER')
    monkeypatch.setattr(report_renderer, 'wrapper_only_retry_section', lambda result: '')
    monkeypatch.setattr(
        report_renderer,
        'target_files_section',
        lambda paths: 'TARGET FILES\n' + '\n'.join(str(path) for path in paths),
    )
    monkeypatch.setattr(report_renderer, 'backup_section', lambda records: 'BACKUP')
    monkeypatch.setattr(report_renderer, 'write_section', lambda records: 'WRITE')
    monkeypatch.setattr(report_renderer, 'command_group_section', lambda title, results: title)
    monkeypatch.setattr(report_renderer, 'full_output_section', lambda results, title: title)
    monkeypatch.setattr(report_renderer, 'failure_section', lambda result: '')
    monkeypatch.setattr(report_renderer, 'render_summary', lambda exit_code, result_label: f'SUMMARY {exit_code} {result_label}')

    result = SimpleNamespace(
        target_project_root=Path('C:/dev/patchops'),
        manifest=SimpleNamespace(files_to_write=[SimpleNamespace(path='tests/example_current.py')]),
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
    )

    text = report_renderer.render_workflow_report(result)
    expected_target = str(Path('C:/dev/patchops') / 'tests' / 'example_current.py')

    assert 'HEADER' in text
    assert 'TARGET FILES' in text
    assert expected_target in text
    assert 'VALIDATION COMMANDS' in text
    assert 'FULL OUTPUT' in text
    assert 'SUMMARY 0 PASS' in text
