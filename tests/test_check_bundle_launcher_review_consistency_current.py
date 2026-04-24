from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from patchops import bundle_review


def test_check_bundle_payload_reflects_rejected_launcher_review(monkeypatch, tmp_path: Path) -> None:
    zip_path = tmp_path / "reject_bundle.zip"
    zip_path.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        bundle_review,
        "_PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD",
        lambda *args, **kwargs: {
            "ok": True,
            "path": str(zip_path),
            "issues": [],
            "issue_count": 0,
            "warnings": [],
            "warning_count": 0,
        },
    )
    monkeypatch.setattr(
        bundle_review,
        "inspect_bundle_payload",
        lambda *args, **kwargs: {
            "ok": False,
            "issues": ["Launcher review rejected this bundle because the launcher matches the risky proof contract."],
            "launcher_review": {
                "status": "reject",
                "launcher_path": "reject_bundle/run_with_patchops.ps1",
                "issue_count": 1,
                "issues": [
                    {
                        "code": "launcher_risk_detected",
                        "message": "Launcher review rejected this bundle because the launcher matches the risky proof contract.",
                        "path": "reject_bundle/run_with_patchops.ps1",
                    }
                ],
            },
            "launcher_status": "reject",
            "launcher_issue_count": 1,
            "launcher_issue_codes": ["launcher_risk_detected"],
        },
    )

    payload = bundle_review.check_bundle_payload(zip_path, requested_profile=None)
    assert payload["ok"] is False
    assert payload["launcher_status"] == "reject"
    assert payload["launcher_issue_codes"] == ["launcher_risk_detected"]
    assert payload["issue_count"] == 1
    assert "risky proof contract" in payload["issues"][0]


def test_cli_check_bundle_main_returns_one_when_launcher_review_rejects(monkeypatch, tmp_path: Path) -> None:
    zip_path = tmp_path / "reject_bundle.zip"
    zip_path.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        bundle_review,
        "_PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD",
        lambda *args, **kwargs: {
            "ok": True,
            "path": str(zip_path),
            "issues": [],
            "issue_count": 0,
            "warnings": [],
            "warning_count": 0,
        },
    )
    monkeypatch.setattr(
        bundle_review,
        "inspect_bundle_payload",
        lambda *args, **kwargs: {
            "ok": False,
            "issues": ["Launcher review rejected this bundle because the launcher matches the risky proof contract."],
            "launcher_review": {
                "status": "reject",
                "launcher_path": "reject_bundle/run_with_patchops.ps1",
                "issue_count": 1,
                "issues": [
                    {
                        "code": "launcher_risk_detected",
                        "message": "Launcher review rejected this bundle because the launcher matches the risky proof contract.",
                        "path": "reject_bundle/run_with_patchops.ps1",
                    }
                ],
            },
            "launcher_status": "reject",
            "launcher_issue_count": 1,
            "launcher_issue_codes": ["launcher_risk_detected"],
        },
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = bundle_review.cli_check_bundle_main([str(zip_path)])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["launcher_status"] == "reject"
    assert payload["launcher_issue_codes"] == ["launcher_risk_detected"]


def test_cli_check_bundle_main_keeps_zero_when_launcher_review_safe(monkeypatch, tmp_path: Path) -> None:
    zip_path = tmp_path / "safe_bundle.zip"
    zip_path.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(
        bundle_review,
        "_PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD",
        lambda *args, **kwargs: {
            "ok": True,
            "path": str(zip_path),
            "issues": [],
            "issue_count": 0,
            "warnings": [],
            "warning_count": 0,
        },
    )
    monkeypatch.setattr(
        bundle_review,
        "inspect_bundle_payload",
        lambda *args, **kwargs: {
            "ok": True,
            "issues": [],
            "launcher_review": {
                "status": "safe",
                "launcher_path": "safe_bundle/run_with_patchops.ps1",
                "issue_count": 0,
                "issues": [],
            },
            "launcher_status": "safe",
            "launcher_issue_count": 0,
            "launcher_issue_codes": [],
        },
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = bundle_review.cli_check_bundle_main([str(zip_path)])

    payload = json.loads(buffer.getvalue())
    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["launcher_status"] == "safe"
