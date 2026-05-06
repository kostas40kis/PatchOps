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


def test_latest_desktop_report_proxy_compares_equal_to_selected_path(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader import report_resolver as rr

    desktop = tmp_path / "fake_desktop"
    desktop.mkdir()

    older = desktop / "older.txt"
    newer = desktop / "newer.txt"
    older.write_text("older\n", encoding="utf-8")
    newer.write_text("newer\n", encoding="utf-8")

    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))

    latest = rr.latest_desktop_report(desktop_dir=desktop, pattern="*.txt")

    assert latest == newer
    assert latest == newer.resolve()
    assert Path(os.fspath(latest)) == newer.resolve()
    assert str(_field(latest, "path", "report_path", "selected_report_path", default=latest)) == str(newer.resolve())


def test_latest_desktop_report_pathlike_proxy_still_skips_empty_newest(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader import report_resolver as rr

    desktop = tmp_path / "fake_desktop"
    desktop.mkdir()

    older_valid = desktop / "older_valid.txt"
    newest_empty = desktop / "newest_empty.txt"

    older_valid.write_text("older valid\n", encoding="utf-8")
    newest_empty.write_text("", encoding="utf-8")

    os.utime(older_valid, (1000, 1000))
    os.utime(newest_empty, (2000, 2000))

    latest = rr.latest_desktop_report(desktop_dir=desktop, pattern="*.txt")

    assert latest == older_valid.resolve()
    assert Path(os.fspath(latest)) == older_valid.resolve()

    recovered = rr.resolve_report(
        desktop_dir=str(desktop),
        latest_desktop_recovery=True,
        pattern="*.txt",
    )

    assert str(_field(recovered, "path", "report_path", "selected_report_path")) == str(older_valid.resolve())
    assert str(_field(recovered, "resolution_mode", "resolver_mode")) == "latest_desktop_recovery"
    assert int(_field(recovered, "stable_observation_count", default=0)) >= 2
