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


def test_latest_desktop_report_skips_newest_empty_file_and_writes_resolved_report_path(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader import report_resolver as rr

    desktop = tmp_path / "fake_desktop"
    desktop.mkdir()

    older_valid = desktop / "u2_01pb_old_valid_report.txt"
    newest_empty = desktop / "u2_01pb_newest_empty_report.txt"

    older_valid.write_text("PATCHOPS REPORT\nSUMMARY\nExitCode : 0\nResult   : PASS\n", encoding="utf-8")
    newest_empty.write_text("", encoding="utf-8")

    older_time = 1_700_000_000
    newer_time = older_time + 100
    os.utime(older_valid, (older_time, older_time))
    os.utime(newest_empty, (newer_time, newer_time))

    latest = rr.latest_desktop_report(desktop_dir=str(desktop), pattern="u2_01pb_*.txt")
    latest_path = str(_field(latest, "path", "report_path", "selected_report_path"))
    assert latest_path == str(older_valid.resolve())

    recovered = rr.resolve_report(
        desktop_dir=str(desktop),
        latest_desktop_recovery=True,
        pattern="u2_01pb_*.txt",
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

    assert "REPORT RESOLUTION" in combined
    assert "REPORT RESOLVER" in combined
    assert "stable_observation_count" in combined
    assert "resolved_report" in combined
    assert str(older_valid.resolve()) in combined
