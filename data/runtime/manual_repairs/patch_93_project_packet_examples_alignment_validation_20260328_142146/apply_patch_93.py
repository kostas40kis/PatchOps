from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")

TRADER_PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "trader.md"
WRAPPER_PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "wrapper_self_hosted.md"
STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"
LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
TEST_PATH = PROJECT_ROOT / "tests" / "test_project_packet_examples_current.py"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def upsert_block(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker, start_index) + len(end_marker)
        new_text = text[:start_index] + block + text[end_index:]
    else:
        if text and not text.endswith("\\n"):
            text += "\\n"
        if text:
            text += "\\n"
        new_text = text + block
    path.write_text(new_text.rstrip() + "\\n", encoding="utf-8")


trader_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH93_TRADER_PACKET:START -->
    ## Maintained packet example reminder

    This trader packet remains the first serious maintained target-project example.

    It should continue to keep these things explicit:

    - target root: `C:\\dev\\trader`
    - wrapper root: `C:\\dev\\patchops`
    - selected profile
    - what must remain outside PatchOps
    - next recommended action
    - handoff first when work is already in progress
    <!-- PATCHOPS_PATCH93_TRADER_PACKET:END -->
    """
)

wrapper_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH93_WRAPPER_PACKET:START -->
    ## Maintained self-hosted packet reminder

    This wrapper self-hosted packet remains the maintained target-facing packet for PatchOps acting as its own current target.

    It should continue to keep these things explicit:

    - target root: `C:\\dev\\patchops`
    - wrapper root: `C:\\dev\\patchops`
    - selected profile
    - what must remain outside PatchOps
    - next recommended action
    - handoff first when work is already in progress
    <!-- PATCHOPS_PATCH93_WRAPPER_PACKET:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH93_STATUS:START -->
    ## Patch 93 - project-packet examples alignment validation

    ### Current state

    - Patch 93 adds a narrow validation surface for the maintained project-packet examples.
    - The trader packet and the wrapper self-hosted packet now both keep the core packet-example reminders explicit:
      - roots,
      - selected profile,
      - target boundary wording,
      - next recommended action,
      - handoff-first continuation when work is already in progress.

    ### Why this matters

    - the maintained packet examples stay aligned with the packet contract and onboarding story,
    - the first serious target packet and the self-hosted packet remain usable as operator-facing references,
    - the repo continues through maintenance validation rather than redesign.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the packet layer is already shipped and the main risk is wording drift.
    <!-- PATCHOPS_PATCH93_STATUS:END -->
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH93_LEDGER:START -->
    ## Patch 93

    Patch 93 adds a maintenance validation surface for the maintained project-packet examples.

    It keeps `docs/projects/trader.md` and `docs/projects/wrapper_self_hosted.md` aligned with the packet contract and the current onboarding-versus-continuation interpretation.

    This is a narrow validation patch, not a project-packet redesign.
    <!-- PATCHOPS_PATCH93_LEDGER:END -->
    """
)

test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    from pathlib import Path


    def test_maintained_project_packet_examples_stay_current() -> None:
        trader_text = Path("docs/projects/trader.md").read_text(encoding="utf-8").lower()
        wrapper_text = Path("docs/projects/wrapper_self_hosted.md").read_text(encoding="utf-8").lower()

        required_trader_fragments = [
            "first serious maintained target-project example",
            "c:\\\\dev\\\\trader",
            "c:\\\\dev\\\\patchops",
            "selected profile",
            "what must remain outside patchops",
            "next recommended action",
            "handoff first when work is already in progress",
        ]
        for fragment in required_trader_fragments:
            assert fragment in trader_text

        required_wrapper_fragments = [
            "maintained target-facing packet for patchops acting as its own current target",
            "c:\\\\dev\\\\patchops",
            "selected profile",
            "what must remain outside patchops",
            "next recommended action",
            "handoff first when work is already in progress",
        ]
        for fragment in required_wrapper_fragments:
            assert fragment in wrapper_text
    """
)

upsert_block(
    TRADER_PACKET_PATH,
    "<!-- PATCHOPS_PATCH93_TRADER_PACKET:START -->",
    "<!-- PATCHOPS_PATCH93_TRADER_PACKET:END -->",
    trader_block,
)

upsert_block(
    WRAPPER_PACKET_PATH,
    "<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:START -->",
    "<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:END -->",
    wrapper_block,
)

upsert_block(
    STATUS_PATH,
    "<!-- PATCHOPS_PATCH93_STATUS:START -->",
    "<!-- PATCHOPS_PATCH93_STATUS:END -->",
    status_block,
)

upsert_block(
    LEDGER_PATH,
    "<!-- PATCHOPS_PATCH93_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH93_LEDGER:END -->",
    ledger_block,
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

print(f"UPDATED: {TRADER_PACKET_PATH}")
print(f"UPDATED: {WRAPPER_PACKET_PATH}")
print(f"UPDATED: {STATUS_PATH}")
print(f"UPDATED: {LEDGER_PATH}")
print(f"WROTE: {TEST_PATH}")