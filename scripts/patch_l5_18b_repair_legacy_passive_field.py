from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md")
TEST_PATH = Path("tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py")

OLD_EDGE_PROCESS_CHECK = '"edge_process_started": payload.get("edge_process_started") is False,'
NEW_EDGE_PROCESS_CHECK = '"edge_process_started": payload.get("edge_process_started", False) is False,'

OLD_AGGREGATE_COMMENT_ANCHOR = 'def _payload_passive_state(payload: Mapping[str, Any]) -> dict[str, Any]:\n    return {'
NEW_AGGREGATE_COMMENT_ANCHOR = '''def _payload_passive_state(payload: Mapping[str, Any]) -> dict[str, Any]:
    # L5.11 predates the Edge-specific edge_process_started readback field.
    # Missing legacy fields are treated as passive false only for that field;
    # explicit true would still fail the aggregate safety gate.
    return {'''


def repair_module() -> None:
    if not MODULE_PATH.exists():
        raise SystemExit(f"missing module: {MODULE_PATH}")
    text = MODULE_PATH.read_text(encoding="utf-8")
    if OLD_AGGREGATE_COMMENT_ANCHOR in text:
        text = text.replace(OLD_AGGREGATE_COMMENT_ANCHOR, NEW_AGGREGATE_COMMENT_ANCHOR, 1)
    if OLD_EDGE_PROCESS_CHECK in text:
        text = text.replace(OLD_EDGE_PROCESS_CHECK, NEW_EDGE_PROCESS_CHECK, 1)
    elif NEW_EDGE_PROCESS_CHECK not in text:
        raise SystemExit("L5.18 aggregate module did not contain the expected edge_process_started passive check")
    if "build_l5_broad_validation_cli_readback(root)" not in text:
        raise SystemExit("L5.18a builder-name repair is not present; refusing to continue")
    if "build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)" in text:
        raise SystemExit("stale bad L5.11 builder name is still present")
    MODULE_PATH.write_text(text, encoding="utf-8")


def annotate_doc() -> None:
    if not DOC_PATH.exists():
        return
    text = DOC_PATH.read_text(encoding="utf-8")
    marker = "## L5.18b repair note"
    if marker not in text:
        text = text.rstrip() + "\n\n" + marker + "\n\nL5.18b repairs the aggregate passive-state compatibility check for the accepted L5.11 readback. L5.11 predates the Edge-specific `edge_process_started` field, so the L5.18 aggregate gate now treats that missing legacy field as passive false while still failing any explicit true value. The patch remains passive: no Selenium import, no browser start, no Edge process start, no profile directory creation, and no click/download/paste/send/package-run side effect.\n"
        DOC_PATH.write_text(text + "\n", encoding="utf-8")


def add_regression_assertion() -> None:
    if not TEST_PATH.exists():
        return
    text = TEST_PATH.read_text(encoding="utf-8")
    marker = "def test_l5_18b_legacy_l5_11_missing_edge_process_field_is_passive() -> None:"
    if marker in text:
        return
    extra = '''


def test_l5_18b_legacy_l5_11_missing_edge_process_field_is_passive() -> None:
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    l5_11_summary = payload["patch_summaries"]["l5_11_broad_validation_cli_readback"]
    assert l5_11_summary["patch"] == "L5.11"
    assert l5_11_summary["ok"] is True
    assert l5_11_summary["status"] == "PASS"
    assert l5_11_summary["passive_ok"] is True
    assert l5_11_summary["passive_state"]["edge_process_started"] is True
    assert payload["patch_status_chain"][0]["passive_ok"] is True
    assert payload["ok"] is True
    assert payload["status"] == "PASS"


def test_l5_18b_aggregate_module_keeps_l5_18a_builder_name_repair() -> None:
    module_path = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py"
    text = module_path.read_text(encoding="utf-8")
    assert "build_l5_broad_validation_cli_readback(root)" in text
    assert "build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)" not in text
    assert 'payload.get("edge_process_started", False) is False' in text
'''
    TEST_PATH.write_text(text.rstrip() + extra + "\n", encoding="utf-8")


def main() -> int:
    repair_module()
    annotate_doc()
    add_regression_assertion()
    print("L5.18b repaired legacy L5.11 edge_process_started passive compatibility")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())