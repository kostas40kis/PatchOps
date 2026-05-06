from __future__ import annotations

import os
from pathlib import Path


def _field(obj, *names: str, default=""):
    for name in names:
        if hasattr(obj, name):
            return getattr(obj, name)
    if hasattr(obj, "to_payload"):
        payload = obj.to_payload()
        if isinstance(payload, dict):
            for name in names:
                if name in payload:
                    return payload[name]
    return default


def test_latest_desktop_report_skips_whitespace_only_newest_report(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader import report_resolver as rr

    desktop = tmp_path / "fake_desktop"
    desktop.mkdir()

    older_valid = desktop / "u2_01pd_old_valid_report.txt"
    newest_blank = desktop / "u2_01pd_newest_blank_report.txt"

    older_valid.write_text("PATCHOPS REPORT\nSUMMARY\nExitCode : 0\nResult   : PASS\n", encoding="utf-8")
    newest_blank.write_text("\r\n\t \n", encoding="utf-8")

    os.utime(older_valid, (1000, 1000))
    os.utime(newest_blank, (2000, 2000))

    latest = rr.latest_desktop_report(desktop_dir=str(desktop), pattern="u2_01pd_*.txt")
    latest_path = str(_field(latest, "path", "report_path", "selected_report_path", default=latest))

    assert latest == older_valid.resolve()
    assert latest_path == str(older_valid.resolve())

    recovered = rr.resolve_report(
        desktop_dir=str(desktop),
        latest_desktop_recovery=True,
        pattern="u2_01pd_*.txt",
    )
    recovered_path = str(_field(recovered, "path", "report_path", "selected_report_path"))

    assert recovered_path == str(older_valid.resolve())
    assert str(_field(recovered, "resolution_mode", "resolver_mode")) == "latest_desktop_recovery"
    assert int(_field(recovered, "stable_observation_count", default=0)) >= 2

    evidence_dir = tmp_path / "evidence"
    rr.write_resolved_report_evidence(recovered, output_dir=str(evidence_dir))

    combined = "\n".join(
        p.read_text(encoding="utf-8", errors="replace")
        for p in evidence_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".txt", ".json", ".log"}
    )

    assert "resolved_report" in combined
    assert str(older_valid.resolve()) in combined
    assert str(newest_blank.resolve()) not in combined
