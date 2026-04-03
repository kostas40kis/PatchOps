from __future__ import annotations

import re
import textwrap
from pathlib import Path


PROJECT_ROOT = Path(r"C:\dev\patchops")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def upsert_marked_block(path: Path, start_marker: str, end_marker: str, body: str) -> None:
    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    text = read_text(path)
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)

    if pattern.search(text):
        updated = pattern.sub(block, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"

    write_text(path, updated)


def patch_tests() -> str:
    path = PROJECT_ROOT / "tests" / "test_final_maintenance_mode_docs.py"
    text = textwrap.dedent(
        """
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def test_readme_keeps_final_maintenance_posture_visible() -> None:
            text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

            assert "## Final maintenance posture" in text
            assert "maintained utility rather than an open-ended architecture buildout" in text
            assert "handoff/current_handoff.md" in text
            assert "docs/finalization_master_plan.md" in text
            assert "maintenance-mode wrapper" in text


        def test_llm_usage_keeps_final_maintenance_reading_order_visible() -> None:
            text = (PROJECT_ROOT / "docs" / "llm_usage.md").read_text(encoding="utf-8")

            assert "## Final maintenance-mode reading order" in text
            assert "handoff/current_handoff.md" in text
            assert "docs/projects/<project_name>.md" in text
            assert "verify reality," in text
            assert "repair narrowly," in text
            assert "docs/finalization_master_plan.md" in text


        def test_operator_quickstart_keeps_final_split_visible() -> None:
            text = (PROJECT_ROOT / "docs" / "operator_quickstart.md").read_text(encoding="utf-8")

            assert "## Final maintenance-mode quickstart" in text
            assert "### Already-running PatchOps work" in text
            assert "### Brand-new target onboarding" in text
            assert "Read the handoff bundle first when it exists." in text
            assert "docs/finalization_master_plan.md" in text


        def test_project_status_tracks_post_f4_state() -> None:
            text = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")

            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "## Patch 128 - active-work continuation flow proof" in text
            assert "latest confirmed green head: Patch 128" in text
            assert "remaining finalization sequence is F5 through F8, not a redesign wave" in text
            assert "maintenance / refinement posture" in text


        def test_finalization_master_plan_tracks_post_f4_state() -> None:
            text = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

            assert "- **Latest confirmed green head:** Patch 128" in text
            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "## Patch 128 - prove active-work continuation flow" in text
            assert "- **F5 — prove the new-target onboarding flow**" in text
            assert "finished enough to freeze" in text
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_final_maintenance_mode_docs.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 128A

        Patch 128A repairs the two stale maintenance-doc assertions left behind after Patch 128 moved the green head from Patch 127 to Patch 128.

        This patch does not change the continuation flow itself.
        It only updates `tests/test_final_maintenance_mode_docs.py` so the maintenance-doc test layer matches the current post-F4 state.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128A_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH128A_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 128A - post-F4 maintenance-doc test repair

        Patch 128A repairs the stale Patch 127 expectations inside the maintenance-doc validation layer after Patch 128 advanced the current green head.

        This is a narrow test-alignment repair.
        It does not change handoff behavior, onboarding behavior, or finalization posture.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128A_STATUS:START -->",
        "<!-- PATCHOPS_PATCH128A_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        patch_tests(),
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
