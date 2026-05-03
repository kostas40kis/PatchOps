from __future__ import annotations

from pathlib import Path

TEST_PATH = Path("tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md")

OLD_NO_AUTH_ASSERTS = '''    l5_26_no_auth = no_auth["l5_26_summary"]
    assert l5_26_no_auth["ok"] is True
    assert l5_26_no_auth["status"] == "PASS"
    assert l5_26_no_auth["patch"] == "L5.26"
'''

NEW_NO_AUTH_ASSERTS = '''    l5_26_no_auth = no_auth["l5_26_summary"]
    # L5.27 deliberately feeds L5.26 a default Edge profile here. L5.26 may
    # report the expected default-profile refusal, but it must remain passive.
    assert l5_26_no_auth["patch"] == "L5.26"
    assert l5_26_no_auth["command_name"] == SOURCE_COMMAND
    assert l5_26_no_auth["default_profile_forbidden"] is True
    assert l5_26_no_auth["default_profile_path_rejected"] is True
    assert l5_26_no_auth["status"] in {"PASS", "FAIL"}
'''

DOC_MARKER = """

## L5.27d stale repair-test expectation repair

L5.27d repairs the stale L5.27a regression test expectation left behind after L5.27c. L5.27c correctly made the L5.27 readback accept wrapped L5.26 when L5.26 safely rejects a deliberately supplied default Microsoft Edge profile. The old L5.27a test still expected wrapped L5.26 to report `ok: true` and `status: PASS` for that default-profile input. L5.27d updates that test to assert the real invariant instead: L5.26 may refuse the default profile, but it must remain passive and must not start a browser, import Selenium, create a profile, click/download, paste/send, or run a package.

If accepted, continue with:

`L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract`
"""


def main() -> int:
    if not TEST_PATH.exists():
        raise SystemExit(f"missing test file: {TEST_PATH}")

    text = TEST_PATH.read_text(encoding="utf-8")
    if OLD_NO_AUTH_ASSERTS in text:
        text = text.replace(OLD_NO_AUTH_ASSERTS, NEW_NO_AUTH_ASSERTS, 1)
        TEST_PATH.write_text(text, encoding="utf-8")
        print("L5.27d repaired stale L5.27a no-auth wrapped-L5.26 expectation")
    elif NEW_NO_AUTH_ASSERTS in text:
        print("L5.27d stale L5.27a no-auth expectation already repaired")
    else:
        raise SystemExit("expected stale L5.27a no-auth wrapped-L5.26 assertion block not found")

    if DOC_PATH.exists():
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        if "## L5.27d stale repair-test expectation repair" not in doc_text:
            DOC_PATH.write_text(doc_text.rstrip() + DOC_MARKER, encoding="utf-8")
            print("L5.27d documentation repair note appended")
        else:
            print("L5.27d documentation repair note already present")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())