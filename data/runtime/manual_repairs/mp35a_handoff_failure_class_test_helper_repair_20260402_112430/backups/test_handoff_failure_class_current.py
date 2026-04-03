from __future__ import annotations

from pathlib import Path

from patchops.failure_categories import normalize_failure_category
from patchops.handoff import export_handoff_bundle
from tests.test_handoff import _read_json, _write_apply_report


def test_export_handoff_bundle_keeps_normalized_failure_class_for_target_failure(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="target_project_failure",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    expected = normalize_failure_category("target_project_failure")
    assert payload["failure_class"] == expected
    assert current_handoff["repo_state"]["failure_class"] == expected
    assert latest_index["failure_class"] == expected
    assert f"failure class: {expected}" in next_prompt.lower()


def test_export_handoff_bundle_normalizes_legacy_suspicious_label_for_continuation(tmp_path: Path) -> None:
    report_path = _write_apply_report(
        tmp_path,
        result_label="FAIL",
        failure_category="suspicious/ambiguous run",
    )
    payload = export_handoff_bundle(report_path=report_path, wrapper_project_root=tmp_path)

    handoff_root = tmp_path / "handoff"
    current_handoff = _read_json(handoff_root / "current_handoff.json")
    latest_index = _read_json(handoff_root / "latest_report_index.json")
    next_prompt = (handoff_root / "next_prompt.txt").read_text(encoding="utf-8")

    expected = normalize_failure_category("suspicious/ambiguous run")
    assert payload["failure_class"] == expected
    assert current_handoff["repo_state"]["failure_class"] == expected
    assert latest_index["failure_class"] == expected
    assert f"failure class: {expected}" in next_prompt.lower()
