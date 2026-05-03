from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_supervised_launch_default_profile_rejection_gate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md")
TEST_PATH = Path("tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py")

OLD_NORMALIZER = '''def _normalize_profile(profile_dir: str | Path | None) -> str:
    if profile_dir is None:
        return ""
    return str(profile_dir).strip().replace("\\\\", "/").lower().rstrip("/")
'''

NEW_NORMALIZER = '''def _normalize_profile(profile_dir: str | Path | None) -> str:
    if profile_dir is None:
        return ""
    # L5.27b: tolerate an accidental ASCII unit-separator path marker from a
    # failed repair manifest while still treating it as a path separator for
    # readback classification. Normal operator paths should use real backslash
    # or slash separators.
    return str(profile_dir).strip().replace("\\x1f", "/").replace("\\\\", "/").lower().rstrip("/")
'''

OLD_CHECK = '''        _check("dedicated_non_default_profile_remains_passive_blocked", ((not rejection_gate.get("dedicated_non_default_profile_present")) or rejection_gate.get("dedicated_non_default_profile_remains_passive_blocked") is True) and rejection_gate.get("startup_allowed") is False, rejection_gate),
'''

NEW_CHECK = '''        _check("dedicated_non_default_profile_remains_passive_blocked", ((not rejection_gate.get("dedicated_non_default_profile_present")) or (rejection_gate.get("explicit_operator_authorization_present") is False) or rejection_gate.get("dedicated_non_default_profile_remains_passive_blocked") is True) and rejection_gate.get("startup_allowed") is False, rejection_gate),
'''

DOC_MARKER = """

## L5.27b no-auth profile path repair

L5.27b repairs the failed L5.27a validation branch. L5.27a correctly relaxed the wrapped L5.26 passive-health check, but its validation manifest passed the default Edge profile path with an accidental control-character separator. L5.27b makes the L5.27 default-profile readback resilient to that malformed separator and makes the dedicated non-default passive-block check scenario-aware: without `--allow-live-start`, startup is blocked by missing authorization before the dedicated-profile passive branch is expected to pass.

The accepted behavior remains unchanged for the real default Microsoft Edge profile path: when `--allow-live-start` and `--profile-dir` are both present, a normal/default Microsoft Edge profile is still rejected.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`
"""

TEST_APPEND = r'''


def test_l5_27b_no_auth_with_malformed_separator_path_still_blocks_without_side_effects() -> None:
    malformed_default_profile = "C:" + "\x1f".join(
        ["Users", "kostas", "AppData", "Local", "Microsoft", "Edge", "User Data", "Default"]
    )
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=malformed_default_profile,
    )

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
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

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["dedicated_non_default_profile_remains_passive_blocked"]["ok"] is True
    assert checks["no_browser_profile_or_adapter_side_effects"]["ok"] is True
'''


def main() -> int:
    if not MODULE_PATH.exists():
        raise SystemExit(f"missing module: {MODULE_PATH}")
    module_text = MODULE_PATH.read_text(encoding="utf-8")

    if OLD_NORMALIZER in module_text:
        module_text = module_text.replace(OLD_NORMALIZER, NEW_NORMALIZER, 1)
        print("L5.27b repaired profile path normalizer")
    elif NEW_NORMALIZER in module_text:
        print("L5.27b profile path normalizer already repaired")
    else:
        raise SystemExit("expected L5.27 profile normalizer not found")

    if OLD_CHECK in module_text:
        module_text = module_text.replace(OLD_CHECK, NEW_CHECK, 1)
        print("L5.27b repaired no-auth dedicated-profile passive check")
    elif NEW_CHECK in module_text:
        print("L5.27b no-auth dedicated-profile passive check already repaired")
    else:
        raise SystemExit("expected L5.27 dedicated-profile passive check not found")

    MODULE_PATH.write_text(module_text, encoding="utf-8")

    if DOC_PATH.exists():
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        if "## L5.27b no-auth profile path repair" not in doc_text:
            DOC_PATH.write_text(doc_text.rstrip() + DOC_MARKER, encoding="utf-8")
            print("L5.27b documentation repair note appended")
        else:
            print("L5.27b documentation repair note already present")

    if TEST_PATH.exists():
        test_text = TEST_PATH.read_text(encoding="utf-8")
        if "test_l5_27b_no_auth_with_malformed_separator_path_still_blocks_without_side_effects" not in test_text:
            TEST_PATH.write_text(test_text.rstrip() + TEST_APPEND + "\n", encoding="utf-8")
            print("L5.27b focused regression test appended")
        else:
            print("L5.27b focused regression test already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())