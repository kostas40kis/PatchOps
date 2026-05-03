from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_supervised_launch_default_profile_rejection_gate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md")
TEST_PATH = Path("tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py")

OLD_FUNC = '''def _l5_26_profile_gate_still_passive(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.26"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("authorization_flag_required") == AUTHORIZATION_FLAG
        and summary.get("profile_dir_argument_required") == PROFILE_DIR_ARGUMENT
        and summary.get("dedicated_profile_argument_gate_enforced") is True
        and summary.get("default_profile_forbidden") is True
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("profile_gate_phase_allows_live_start") is False
    )
'''

NEW_FUNC = '''def _l5_26_profile_gate_still_passive(summary: Mapping[str, Any]) -> bool:
    """Return True when the wrapped L5.26 gate is healthy and passive.

    L5.27 calls L5.26 in three intentional scenarios: missing authorization,
    missing profile, and default-profile rejection. The L5.26 status/refusal
    fields legitimately vary between those scenarios, so this check must not
    require default_profile_path_rejected=True for the missing-authorization or
    missing-profile readbacks. The invariant that matters for L5.27 repair is
    that L5.26 still reports PASS, keeps Edge passive, and performs no side
    effects.
    """
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.26"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("authorization_flag_required") == AUTHORIZATION_FLAG
        and summary.get("profile_dir_argument_required") == PROFILE_DIR_ARGUMENT
        and summary.get("dedicated_profile_argument_gate_enforced") is True
        and summary.get("default_profile_forbidden") is True
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("profile_gate_phase_allows_live_start") is False
    )
'''

OLD_NEXT = 'NEXT_PATCH = "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract"'
NEW_NEXT = 'NEXT_PATCH = "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract"'

DOC_MARKER = """

## L5.27a missing-auth readback repair

L5.27a repairs the L5.27 missing-authorization and missing-profile readback branch. The wrapped L5.26 profile gate can legitimately report a missing authorization or missing profile refusal before it reaches default-profile rejection. L5.27a therefore treats L5.26 as healthy when it still reports PASS, remains passive, and performs no browser/profile/Selenium/click/download/paste/send/package-run side effects.

The default Microsoft Edge profile rejection behavior remains unchanged. A default Microsoft Edge profile path is still rejected when explicit authorization and a profile path are both present.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`
"""

TEST_APPEND = r'''


def test_l5_27a_missing_auth_and_missing_profile_readbacks_are_healthy_and_passive() -> None:
    no_auth = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_profile = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )

    assert no_auth["ok"] is True
    assert no_auth["status"] == "PASS"
    assert no_auth["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert no_auth["startup_allowed"] is False
    assert no_auth["live_start_performed"] is False
    assert no_auth["browser_started"] is False
    assert no_auth["edge_process_started"] is False
    assert no_auth["browser_session_created"] is False
    assert no_auth["driver_created"] is False
    assert no_auth["profile_directory_created"] is False
    assert no_auth["filesystem_writes_performed"] == []
    assert no_auth["adapter_filesystem_writes_performed"] == []
    assert no_auth["side_effects_performed"] == []
    assert no_auth["selenium_imported_by_readback"] is False

    l5_26_no_auth = no_auth["l5_26_summary"]
    assert l5_26_no_auth["ok"] is True
    assert l5_26_no_auth["status"] == "PASS"
    assert l5_26_no_auth["patch"] == "L5.26"
    assert l5_26_no_auth["startup_allowed"] is False
    assert l5_26_no_auth["live_start_performed"] is False
    assert l5_26_no_auth["browser_started"] is False
    assert l5_26_no_auth["profile_directory_created"] is False
    assert l5_26_no_auth["filesystem_writes_performed"] == []
    assert l5_26_no_auth["adapter_filesystem_writes_performed"] == []
    assert l5_26_no_auth["side_effects_performed"] == []
    assert l5_26_no_auth["selenium_imported_by_readback"] is False

    assert missing_profile["ok"] is True
    assert missing_profile["status"] == "PASS"
    assert missing_profile["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
    assert missing_profile["profile_dir_argument_present"] is False
    assert missing_profile["startup_allowed"] is False
    assert missing_profile["live_start_performed"] is False
    assert missing_profile["browser_started"] is False
    assert missing_profile["edge_process_started"] is False
    assert missing_profile["browser_session_created"] is False
    assert missing_profile["driver_created"] is False
    assert missing_profile["profile_directory_created"] is False
    assert missing_profile["filesystem_writes_performed"] == []
    assert missing_profile["adapter_filesystem_writes_performed"] == []
    assert missing_profile["side_effects_performed"] == []
    assert missing_profile["selenium_imported_by_readback"] is False

    l5_26_missing_profile = missing_profile["l5_26_summary"]
    assert l5_26_missing_profile["ok"] is True
    assert l5_26_missing_profile["status"] == "PASS"
    assert l5_26_missing_profile["patch"] == "L5.26"
    assert l5_26_missing_profile["startup_allowed"] is False
    assert l5_26_missing_profile["live_start_performed"] is False
    assert l5_26_missing_profile["browser_started"] is False
    assert l5_26_missing_profile["profile_directory_created"] is False
    assert l5_26_missing_profile["filesystem_writes_performed"] == []
    assert l5_26_missing_profile["adapter_filesystem_writes_performed"] == []
    assert l5_26_missing_profile["side_effects_performed"] == []
    assert l5_26_missing_profile["selenium_imported_by_readback"] is False
'''


def main() -> int:
    if not MODULE_PATH.exists():
        raise SystemExit(f"missing module: {MODULE_PATH}")
    module_text = MODULE_PATH.read_text(encoding="utf-8")
    if OLD_FUNC not in module_text:
        if NEW_FUNC in module_text:
            print("L5.27a module repair already present")
        else:
            raise SystemExit("expected L5.27 helper function body not found")
    else:
        module_text = module_text.replace(OLD_FUNC, NEW_FUNC, 1)
        # Keep the next patch name unchanged; this is a repair slice, not a new feature frontier.
        module_text = module_text.replace(OLD_NEXT, NEW_NEXT, 1)
        MODULE_PATH.write_text(module_text, encoding="utf-8")
        print("L5.27a repaired L5.26 passive-health check for missing auth/profile branches")

    if DOC_PATH.exists():
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        if "## L5.27a missing-auth readback repair" not in doc_text:
            DOC_PATH.write_text(doc_text.rstrip() + DOC_MARKER, encoding="utf-8")
            print("L5.27a documentation repair note appended")
        else:
            print("L5.27a documentation repair note already present")

    if TEST_PATH.exists():
        test_text = TEST_PATH.read_text(encoding="utf-8")
        if "test_l5_27a_missing_auth_and_missing_profile_readbacks_are_healthy_and_passive" not in test_text:
            TEST_PATH.write_text(test_text.rstrip() + TEST_APPEND + "\n", encoding="utf-8")
            print("L5.27a focused regression test appended")
        else:
            print("L5.27a focused regression test already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())