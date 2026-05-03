from __future__ import annotations

from pathlib import Path

TEST_PATH = Path("tests/test_l8_01_edge_executable_probe_safety_preflight_passive_contract_current.py")
VALIDATE_PATH = Path("scripts/patch_l8_01_brief_validate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md")
MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_passive_contract.py")
REPAIR_NOTE = "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok."


def _replace_once(text: str, old: str, new: str, path: Path) -> str:
    if old not in text:
        raise RuntimeError(f"Expected text not found in {path}: {old!r}")
    return text.replace(old, new, 1)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def repair_test() -> None:
    text = TEST_PATH.read_text(encoding="utf-8")
    text = _replace_once(
        text,
        '    assert payload["ok"] is False\n    assert payload["status"] == "FAIL"\n',
        '    assert payload["ok"] is True\n    assert payload["status"] == "PASS"\n',
        TEST_PATH,
    )
    text = _replace_once(
        text,
        '    assert payload["edge_executable_probe_safety_preflight_passed"] is False\n    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False\n',
        '    assert payload["edge_executable_probe_safety_preflight_passed"] is False\n    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False\n    assert payload["preflight_blocked_reason"].startswith("L8.1 models safety preflight only")\n',
        TEST_PATH,
    )
    if REPAIR_NOTE not in text:
        marker = '        "preflight alone does not perform a probe",\n'
        text = _replace_once(
            text,
            marker,
            marker + f'        "{REPAIR_NOTE}",\n',
            TEST_PATH,
        )
    _write(TEST_PATH, text)


def repair_validate() -> None:
    text = VALIDATE_PATH.read_text(encoding="utf-8")
    text = _replace_once(
        text,
        '    assert no_auth["ok"] is False\n    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False\n',
        '    assert no_auth["ok"] is True\n    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False\n',
        VALIDATE_PATH,
    )
    text = _replace_once(
        text,
        '    print("PASS no_probe_auth: patch=L8.1 preflight_passed=False probe_execution_allowed=False exe_probe=False")\n',
        '    print("PASS no_probe_auth: patch=L8.1 readback_ok=True preflight_passed=False probe_execution_allowed=False exe_probe=False")\n',
        VALIDATE_PATH,
    )
    _write(VALIDATE_PATH, text)


def repair_doc() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    if REPAIR_NOTE not in text:
        text = _replace_once(
            text,
            "- preflight alone does not perform a probe.\n",
            "- preflight alone does not perform a probe.\n- " + REPAIR_NOTE + "\n",
            DOC_PATH,
        )
    _write(DOC_PATH, text)


def repair_module_doc_requirements() -> None:
    text = MODULE_PATH.read_text(encoding="utf-8")
    if REPAIR_NOTE in text:
        return
    needle = '        "preflight alone does not perform a probe",\n'
    text = _replace_once(
        text,
        needle,
        needle + f'        "{REPAIR_NOTE}",\n',
        MODULE_PATH,
    )
    _write(MODULE_PATH, text)


def main() -> int:
    for path in (TEST_PATH, VALIDATE_PATH, DOC_PATH, MODULE_PATH):
        if not path.exists():
            raise FileNotFoundError(path)
    repair_test()
    repair_validate()
    repair_doc()
    repair_module_doc_requirements()
    print("L8.01a repaired the no-authorization expectation: readback ok, preflight not passed, no probe performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())