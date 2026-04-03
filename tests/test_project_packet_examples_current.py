from __future__ import annotations

from pathlib import Path


def test_maintained_project_packet_examples_stay_current() -> None:
    trader_text = Path("docs/projects/trader.md").read_text(encoding="utf-8").lower()
    wrapper_text = Path("docs/projects/wrapper_self_hosted.md").read_text(encoding="utf-8").lower()

    required_trader_fragments = [
        "first serious maintained target-project example",
        "c:\\dev\\trader",
        "c:\\dev\\patchops",
        "selected profile",
        "what must remain outside patchops",
        "next recommended action",
        "handoff first when work is already in progress",
    ]
    for fragment in required_trader_fragments:
        assert fragment in trader_text

    required_wrapper_fragments = [
        "maintained target-facing packet for patchops acting as its own current target",
        "c:\\dev\\patchops",
        "selected profile",
        "what must remain outside patchops",
        "next recommended action",
        "handoff first when work is already in progress",
    ]
    for fragment in required_wrapper_fragments:
        assert fragment in wrapper_text
