from __future__ import annotations

import re
from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_supervised_launch_default_profile_rejection_gate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md")
TEST_PATH = Path("tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py")

NEW_PASSIVE_FUNC_BLOCK = r'''def _l5_26_profile_gate_still_passive(summary: Mapping[str, Any]) -> bool:
    """Return True when wrapped L5.26 preserves passive safety.

    L5.27 intentionally feeds default-profile candidates into its own default
    rejection gate. The older L5.26 profile gate is allowed to reject that
    default profile, so L5.27 must not require L5.26 to report ok=True for the
    default-profile scenario. The invariant L5.27 needs from L5.26 is that the
    L5.26 surface is still present, reports the expected safety fields, and
    performs no browser/profile/Selenium/click/download/paste/send/package-run
    side effects.
    """
    return (
        summary.get("patch") == "L5.26"
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


def _l5_26_source_gate_acceptable_for_l5_27(summary: Mapping[str, Any]) -> bool:
    """Return True when L5.26 is either PASS or safely rejecting a default profile.

    A PASS L5.26 readback remains the normal case for missing-profile and
    dedicated-profile scenarios. A FAIL L5.26 readback is acceptable only when
    the failure is the expected default-profile refusal and all passive safety
    invariants are still intact.
    """
    if not _l5_26_profile_gate_still_passive(summary):
        return False
    if summary.get("ok") is True and summary.get("status") == STATUS_PASS:
        return True
    return (
        summary.get("status") == STATUS_FAIL
        and summary.get("default_profile_forbidden") is True
        and summary.get("default_profile_path_rejected") is True
        and summary.get("profile_gate_status")
        in {
            "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION",
            "BLOCKED_DEFAULT_PROFILE_FORBIDDEN",
        }
    )
'''

DOC_MARKER = """

## L5.27c wrapped L5.26 semantic repair

L5.27c repairs the remaining L5.27b failure. L5.27 owns default Microsoft Edge profile rejection. The wrapped L5.26 dedicated-profile gate is older and may correctly report FAIL when it is deliberately fed a default Edge profile. L5.27c therefore treats wrapped L5.26 as acceptable when either:

- L5.26 reports PASS and remains passive; or
- L5.26 reports the expected default-profile refusal while still preserving every passive safety invariant.

This keeps the real L5.27 default-profile contract intact: a normal/default Microsoft Edge profile is rejected and startup remains blocked. It also keeps missing authorization, missing profile, and dedicated non-default profile scenarios passive.

No behavior in this repair starts a browser, imports Selenium, creates a driver, creates a profile directory, clicks/downloads, pastes/sends, runs packages, commits, or pushes.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`
"""

TEST_APPEND = r'''


def test_l5_27c_no_auth_real_default_profile_accepts_wrapped_l5_26_default_refusal() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEFAULT_PROFILE,
    )
    checks = {check["name"]: check for check in payload["checks"]}
    wrapped = payload["l5_26_summary"]

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert payload["explicit_operator_authorization_present"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["selenium_imported_by_readback"] is False

    # L5.26 may reject this deliberately supplied default profile, but it must
    # remain fully passive and safe.
    assert wrapped["patch"] == "L5.26"
    assert wrapped["command_name"] == SOURCE_COMMAND
    assert wrapped["default_profile_forbidden"] is True
    assert wrapped["default_profile_path_rejected"] is True
    assert wrapped["startup_allowed"] is False
    assert wrapped["live_start_performed"] is False
    assert wrapped["browser_started"] is False
    assert wrapped["edge_process_started"] is False
    assert wrapped["browser_session_created"] is False
    assert wrapped["driver_created"] is False
    assert wrapped["profile_directory_created"] is False
    assert wrapped["filesystem_writes_performed"] == []
    assert wrapped["adapter_filesystem_writes_performed"] == []
    assert wrapped["side_effects_performed"] == []
    assert wrapped["selenium_imported_by_readback"] is False

    assert checks["l5_26_edge_profile_gate_still_passes"]["ok"] is True
    assert checks["l5_26_edge_profile_gate_remains_passive"]["ok"] is True
    assert checks["default_profile_path_is_rejected"]["ok"] is True
    assert checks["no_browser_profile_or_adapter_side_effects"]["ok"] is True


def test_l5_27c_authorized_default_profile_still_rejected_without_browser_side_effects() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["explicit_operator_authorization_present"] is True
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is True
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert checks["l5_26_edge_profile_gate_still_passes"]["ok"] is True
    assert checks["l5_26_edge_profile_gate_remains_passive"]["ok"] is True
    assert checks["default_profile_path_is_rejected"]["ok"] is True
'''


def _replace_function_block(text: str) -> str:
    pattern = re.compile(
        r"def _l5_26_profile_gate_still_passive\(summary: Mapping\[str, Any\]\) -> bool:\n.*?\n\ndef _default_rejection_gate_state",
        re.DOTALL,
    )
    replacement = NEW_PASSIVE_FUNC_BLOCK + "\n\ndef _default_rejection_gate_state"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        if "def _l5_26_source_gate_acceptable_for_l5_27" in text:
            return text
        raise SystemExit("expected L5.27 wrapped L5.26 passive helper block not found")
    return updated


def _replace_checks(text: str) -> str:
    old_source = '''        _check("l5_26_edge_profile_gate_still_passes", l5_26_summary.get("ok") is True and l5_26_summary.get("status") == STATUS_PASS, l5_26_summary),'''
    new_source = '''        _check("l5_26_edge_profile_gate_still_passes", _l5_26_source_gate_acceptable_for_l5_27(l5_26_summary), l5_26_summary),'''
    if old_source in text:
        text = text.replace(old_source, new_source, 1)
        print("L5.27c made wrapped L5.26 source gate scenario-aware")
    elif new_source in text:
        print("L5.27c wrapped L5.26 source gate check already repaired")
    else:
        raise SystemExit("expected L5.27 wrapped L5.26 source gate check not found")

    old_default_check = '''        _check("default_profile_path_is_rejected", ((not rejection_gate.get("default_profile_candidate_detected")) or rejection_gate.get("default_profile_rejection_gate_status") == DEFAULT_PROFILE_STATUS) and rejection_gate.get("startup_allowed") is False, rejection_gate),'''
    new_default_check = '''        _check("default_profile_path_is_rejected", ((not rejection_gate.get("default_profile_candidate_detected")) or rejection_gate.get("default_profile_path_rejected") is True) and rejection_gate.get("startup_allowed") is False, rejection_gate),'''
    if old_default_check in text:
        text = text.replace(old_default_check, new_default_check, 1)
        print("L5.27c made default-profile rejection check scenario-aware")
    elif new_default_check in text:
        print("L5.27c default-profile rejection check already repaired")
    else:
        raise SystemExit("expected L5.27 default-profile rejection check not found")

    return text


def main() -> int:
    if not MODULE_PATH.exists():
        raise SystemExit(f"missing module: {MODULE_PATH}")
    module_text = MODULE_PATH.read_text(encoding="utf-8")
    module_text = _replace_function_block(module_text)
    module_text = _replace_checks(module_text)
    MODULE_PATH.write_text(module_text, encoding="utf-8")
    print("L5.27c repaired wrapped L5.26 default-profile semantics")

    if DOC_PATH.exists():
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        if "## L5.27c wrapped L5.26 semantic repair" not in doc_text:
            DOC_PATH.write_text(doc_text.rstrip() + DOC_MARKER, encoding="utf-8")
            print("L5.27c documentation repair note appended")
        else:
            print("L5.27c documentation repair note already present")

    if TEST_PATH.exists():
        test_text = TEST_PATH.read_text(encoding="utf-8")
        if "test_l5_27c_no_auth_real_default_profile_accepts_wrapped_l5_26_default_refusal" not in test_text:
            TEST_PATH.write_text(test_text.rstrip() + TEST_APPEND + "\n", encoding="utf-8")
            print("L5.27c focused regression tests appended")
        else:
            print("L5.27c focused regression tests already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())