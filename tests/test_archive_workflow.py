from patchops.workflows.archive import (
    ARCHIVE_REPORT_SECTIONS,
    ArchiveWorkflowState,
    archive_has_work,
    build_archive_workflow_state,
    render_archive_scope_lines,
    resolve_archive_commands,
)


def test_resolve_archive_commands_keeps_only_mapping_entries() -> None:
    manifest = {
        "archive_commands": [
            {"name": "zip_results", "program": "python", "args": ["archive.py"]},
            "not_a_command",
        ]
    }

    commands = resolve_archive_commands(manifest)

    assert len(commands) == 1
    assert commands[0]["name"] == "zip_results"


def test_build_archive_workflow_state_is_explicit_and_traceable() -> None:
    manifest = {
        "archive_commands": [
            {"name": "zip_results", "program": "python", "args": ["archive.py"]},
            {"name": "move_logs", "program": "powershell", "args": ["-File", "move_logs.ps1"]},
        ],
        "validation_commands": [
            {"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]},
        ],
        "destructive_archive": True,
    }

    state = build_archive_workflow_state(manifest)

    assert isinstance(state, ArchiveWorkflowState)
    assert state.mode == "archive"
    assert state.archive_command_count == 2
    assert state.validation_command_count == 1
    assert state.report_sections == ARCHIVE_REPORT_SECTIONS
    assert state.deterministic_reporting is True
    assert state.destructive is True
    assert state.traceable is True


def test_render_archive_scope_lines_stays_human_readable() -> None:
    state = build_archive_workflow_state({
        "archive_commands": [{"name": "zip_results", "program": "python", "args": ["archive.py"]}],
        "validation_commands": [],
    })

    lines = render_archive_scope_lines(state)

    assert "Scope    : archive workflow" in lines
    assert "Mode     : archive" in lines
    assert "Archive  : 1" in lines
    assert "Validate : 0" in lines
    assert "Evidence : explicit and traceable archive sections" in lines
    assert "Danger   : non-destructive" in lines


def test_archive_has_work_is_false_when_no_archive_commands_exist() -> None:
    state = build_archive_workflow_state({"archive_commands": []})
    assert archive_has_work(state) is False


def test_archive_report_sections_order_is_stable() -> None:
    assert ARCHIVE_REPORT_SECTIONS == (
        "TARGET FILES",
        "BACKUP",
        "ARCHIVE COMMANDS",
        "ARCHIVE OUTPUT",
        "SUMMARY",
    )
