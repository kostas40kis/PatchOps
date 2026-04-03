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


def ensure_replaced(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new)
    if new in text:
        return text
    return text


def upsert_marked_block(path: Path, start_marker: str, end_marker: str, body: str) -> None:
    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    text = read_text(path)
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)

    if pattern.search(text):
        updated = pattern.sub(block, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"

    write_text(path, updated)


def patch_finalization_master() -> str:
    path = PROJECT_ROOT / "docs" / "finalization_master_plan.md"
    text = read_text(path)

    text = ensure_replaced(
        text,
        "- **Latest confirmed green head:** Patch 126",
        "- **Latest confirmed green head:** Patch 127",
    )
    text = ensure_replaced(
        text,
        "- Patch 126 refreshes the self-contained documentation set that a future LLM can use without prior chat history.",
        "- Patch 126 refreshes the self-contained documentation set that a future LLM can use without prior chat history.\n- Patch 127 adds narrow contract-lock validation so the final maintenance posture is protected by tests rather than memory.",
    )
    text = ensure_replaced(
        text,
        "- **F3 — final contract-lock validation sweep**",
        "- **F4 — prove the active-work continuation flow**",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 127 - final contract-lock validation sweep

        Patch 127 is the F3 validation-first patch.

        ### What it locks

        - the final maintenance-mode reading story in `README.md`,
        - the final maintenance-mode takeover story in `docs/llm_usage.md`,
        - the final maintenance-mode quickstart split in `docs/operator_quickstart.md`,
        - the current maintenance posture in `docs/project_status.md`,
        - the freeze/finalization posture in `docs/finalization_master_plan.md`.

        ### Why this matters

        The earlier maintenance wave already tightened:
        - help text contracts,
        - launcher inventory contracts,
        - exact CLI subcommand set contracts,
        - onboarding-versus-continuation boundary wording,
        - project-packet wording.

        This patch adds the missing final layer:
        the maintenance-mode final docs are now protected by explicit tests instead of memory.

        ### Current next action

        - **F4 — prove the active-work continuation flow**

        ### Rule

        This patch locks what is already shipped.
        It does not widen the product.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH127_FINALIZATION_MASTER:START -->",
        "<!-- PATCHOPS_PATCH127_FINALIZATION_MASTER:END -->",
        block,
    )
    return "docs/finalization_master_plan.md"


def patch_project_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    text = read_text(path)

    text = ensure_replaced(
        text,
        "- latest confirmed green head: Patch 126",
        "- latest confirmed green head: Patch 127",
    )
    text = ensure_replaced(
        text,
        "- the remaining finalization sequence is F3 through F8, not a redesign wave",
        "- the remaining finalization sequence is F4 through F8, not a redesign wave",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 127 - final contract-lock validation sweep

        ### Current state

        - Patch 127 adds narrow maintenance-mode contract tests for the final docs introduced by Patch 126.
        - The final posture is now enforced by tests rather than memory.
        - The repo remains in a maintenance / refinement posture.

        ### What is now explicitly protected

        - `README.md` final maintenance posture wording,
        - `docs/llm_usage.md` final maintenance-mode reading order,
        - `docs/operator_quickstart.md` final maintenance-mode quickstart split,
        - `docs/project_status.md` maintenance posture wording,
        - `docs/finalization_master_plan.md` freeze/finalization posture wording.

        ### Remaining posture

        - continue with F4 through F8,
        - prefer validation-first proof and narrow repair over broader rewrite,
        - keep the repo in maintenance validation rather than redesign.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH127_STATUS:START -->",
        "<!-- PATCHOPS_PATCH127_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 127

        Patch 127 is the final contract-lock validation sweep from the rushed finalization plan.

        It adds narrow tests that protect the maintenance-mode final docs introduced in Patch 126:
        - `README.md`
        - `docs/llm_usage.md`
        - `docs/operator_quickstart.md`
        - `docs/project_status.md`
        - `docs/finalization_master_plan.md`

        This is a validation-first maintenance patch.
        It exists to lock shipped truth rather than widen behavior.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH127_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH127_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def write_tests() -> str:
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


        def test_project_status_tracks_patch_127_final_contract_lock_sweep() -> None:
            text = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")

            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "latest confirmed green head: Patch 127" in text
            assert "remaining finalization sequence is F4 through F8, not a redesign wave" in text
            assert "maintenance / refinement posture" in text


        def test_finalization_master_plan_tracks_post_f3_state() -> None:
            text = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

            assert "- **Latest confirmed green head:** Patch 127" in text
            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "- **F4 — prove the active-work continuation flow**" in text
            assert "finished enough to freeze" in text
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_final_maintenance_mode_docs.py"


def main() -> int:
    changed = [
        patch_finalization_master(),
        patch_project_status(),
        patch_ledger(),
        write_tests(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
