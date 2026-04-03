from patchops.workflows.cleanup import (
    CLEANUP_REPORT_SECTIONS,
    CleanupWorkflowState,
    build_cleanup_workflow_state,
    cleanup_has_work,
    render_cleanup_scope_lines,
    resolve_cleanup_commands,
)


def test_resolve_cleanup_commands_keeps_only_mapping_entries() -> None:
    manifest = {
        "cleanup_commands": [
            {"name": "remove_temp", "program": "python", "args": ["cleanup.py"]},
            "not_a_command",
        ]
    }

    commands = resolve_cleanup_commands(manifest)

    assert len(commands) == 1
    assert commands[0]["name"] == "remove_temp"


def test_build_cleanup_workflow_state_is_explicit_and_deterministic() -> None:
    manifest = {
        "cleanup_commands": [
            {"name": "remove_temp", "program": "python", "args": ["cleanup.py"]},
            {"name": "trim_logs", "program": "powershell", "args": ["-File", "trim.ps1"]},
        ],
        "validation_commands": [
            {"name": "pytest", "program": "python", "args": ["-m", "pytest", "-q"]},
        ],
        "destructive_cleanup": True,
    }

    state = build_cleanup_workflow_state(manifest)

    assert isinstance(state, CleanupWorkflowState)
    assert state.mode == "cleanup"
    assert state.cleanup_command_count == 2
    assert state.validation_command_count == 1
    assert state.report_sections == CLEANUP_REPORT_SECTIONS
    assert state.deterministic_reporting is True
    assert state.destructive is True


def test_render_cleanup_scope_lines_stays_human_readable() -> None:
    state = build_cleanup_workflow_state({
        "cleanup_commands": [{"name": "remove_temp", "program": "python", "args": ["cleanup.py"]}],
        "validation_commands": [],
    })

    lines = render_cleanup_scope_lines(state)

    assert "Scope    : cleanup workflow" in lines
    assert "Mode     : cleanup" in lines
    assert "Cleanup  : 1" in lines
    assert "Validate : 0" in lines
    assert "Evidence : explicit and deterministic cleanup sections" in lines
    assert "Danger   : non-destructive" in lines


def test_cleanup_has_work_is_false_when_no_cleanup_commands_exist() -> None:
    state = build_cleanup_workflow_state({"cleanup_commands": []})
    assert cleanup_has_work(state) is False


def test_cleanup_report_sections_order_is_stable() -> None:
    assert CLEANUP_REPORT_SECTIONS == (
        "TARGET FILES",
        "BACKUP",
        "CLEANUP COMMANDS",
        "CLEANUP OUTPUT",
        "SUMMARY",
    )
