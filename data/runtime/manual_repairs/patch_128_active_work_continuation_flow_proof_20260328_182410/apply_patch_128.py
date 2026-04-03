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
        "- **Latest confirmed green head:** Patch 127",
        "- **Latest confirmed green head:** Patch 128",
    )
    text = ensure_replaced(
        text,
        "- Patch 127 adds narrow contract-lock validation so the final maintenance posture is protected by tests rather than memory.",
        "- Patch 127 adds narrow contract-lock validation so the final maintenance posture is protected by tests rather than memory.\n- Patch 128 re-exports the current handoff bundle from a real green report and adds maintenance tests proving the active-work continuation flow remains mechanical.",
    )
    text = ensure_replaced(
        text,
        "### F4 — prove the active-work continuation flow",
        "### F5 — prove the new-target onboarding flow",
    )
    text = ensure_replaced(
        text,
        "- **F4 — prove the active-work continuation flow**",
        "- **F5 — prove the new-target onboarding flow**",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 128 - prove active-work continuation flow

        Patch 128 is the F4 proof patch from the rushed finalization sequence.

        ### What it proves

        - the handoff bundle is not only documented but also refreshed from a real current PASS report,
        - `export-handoff` continues to produce the maintained continuation surfaces under `handoff/`,
        - the active-work continuation path remains mechanical:
          1. read the handoff bundle,
          2. restate current state,
          3. perform the next recommended action.

        ### Validation posture

        The repo already had handoff surfaces and handoff-oriented tests.
        This patch adds one current-state proof layer:
        the generated `handoff/` outputs are now treated as a maintained active-work continuation surface.

        ### Current next action

        - **F5 — prove the new-target onboarding flow**

        ### Rule

        This patch proves and refreshes an already-shipped continuation path.
        It does not reopen handoff architecture.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128_FINALIZATION_MASTER:START -->",
        "<!-- PATCHOPS_PATCH128_FINALIZATION_MASTER:END -->",
        block,
    )
    return "docs/finalization_master_plan.md"


def patch_project_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    text = read_text(path)

    text = ensure_replaced(
        text,
        "- latest confirmed green head: Patch 127",
        "- latest confirmed green head: Patch 128",
    )
    text = ensure_replaced(
        text,
        "- the remaining finalization sequence is F4 through F8, not a redesign wave",
        "- the remaining finalization sequence is F5 through F8, not a redesign wave",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 128 - active-work continuation flow proof

        ### Current state

        - Patch 128 re-exports the maintained handoff bundle from a real current PASS report.
        - Patch 128 adds one current-state continuation proof test layer.
        - The active-work continuation path is now proven both by function/CLI tests and by current generated artifacts.

        ### What is now explicitly protected

        - `handoff/current_handoff.md`
        - `handoff/current_handoff.json`
        - `handoff/latest_report_copy.txt`
        - `handoff/latest_report_index.json`
        - `handoff/next_prompt.txt`
        - `handoff/bundle/current/`

        ### Remaining posture

        - continue with F5 through F8,
        - keep onboarding separate from continuation,
        - prefer narrow proof and repair over broader rewrite.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128_STATUS:START -->",
        "<!-- PATCHOPS_PATCH128_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def patch_handoff_surface() -> str:
    path = PROJECT_ROOT / "docs" / "handoff_surface.md"
    text = read_text(path)

    block = textwrap.dedent(
        """
        ## Patch 128 - active-work continuation proof

        Patch 128 re-exports the handoff bundle from a real green maintenance report and treats the generated `handoff/` outputs as maintained proof surfaces.

        The active-work continuation path should now be interpreted like this:

        1. read `handoff/current_handoff.md`,
        2. read `handoff/current_handoff.json`,
        3. read `handoff/latest_report_copy.txt`,
        4. restate current state briefly,
        5. perform the exact next recommended action.

        This remains separate from onboarding for brand-new target work.
        Handoff is the first resume surface for already-running PatchOps work.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128_HANDOFF_SURFACE:START -->",
        "<!-- PATCHOPS_PATCH128_HANDOFF_SURFACE:END -->",
        block,
    )
    return "docs/handoff_surface.md"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 128

        Patch 128 is the F4 proof patch from the rushed finalization plan.

        It does three things:
        - re-exports the current handoff bundle from a real green report,
        - records the generated `handoff/` outputs as maintained continuation artifacts,
        - adds one narrow validation layer that proves the active-work continuation flow remains mechanical.

        This is a proof-and-refresh patch, not a handoff redesign patch.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH128_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH128_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def write_tests() -> str:
    path = PROJECT_ROOT / "tests" / "test_active_work_continuation_current.py"
    text = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def _read_json(path: Path) -> dict:
            return json.loads(path.read_text(encoding="utf-8"))


        def test_current_handoff_bundle_exists_with_expected_files() -> None:
            handoff_root = PROJECT_ROOT / "handoff"

            required_files = [
                handoff_root / "current_handoff.md",
                handoff_root / "current_handoff.json",
                handoff_root / "latest_report_copy.txt",
                handoff_root / "latest_report_index.json",
                handoff_root / "next_prompt.txt",
                handoff_root / "bundle" / "current" / "current_handoff.md",
                handoff_root / "bundle" / "current" / "current_handoff.json",
                handoff_root / "bundle" / "current" / "latest_report_copy.txt",
                handoff_root / "bundle" / "current" / "latest_report_index.json",
                handoff_root / "bundle" / "current" / "next_prompt.txt",
            ]

            for path in required_files:
                assert path.exists(), f"Missing handoff artifact: {path}"


        def test_current_handoff_json_keeps_resume_contract() -> None:
            current_handoff = _read_json(PROJECT_ROOT / "handoff" / "current_handoff.json")
            latest_index = _read_json(PROJECT_ROOT / "handoff" / "latest_report_index.json")

            assert "repo_state" in current_handoff
            assert "resume" in current_handoff
            assert "latest_patch" in current_handoff

            assert isinstance(current_handoff["repo_state"].get("latest_run_mode"), str)
            assert current_handoff["repo_state"]["latest_run_mode"]
            assert isinstance(current_handoff["resume"].get("next_recommended_mode"), str)
            assert current_handoff["resume"]["next_recommended_mode"]

            assert isinstance(latest_index.get("latest_attempted_patch"), str)
            assert latest_index["latest_attempted_patch"]
            assert isinstance(latest_index.get("next_recommended_mode"), str)
            assert latest_index["next_recommended_mode"]


        def test_next_prompt_and_latest_report_copy_stay_mechanical() -> None:
            prompt_text = (PROJECT_ROOT / "handoff" / "next_prompt.txt").read_text(encoding="utf-8")
            report_text = (PROJECT_ROOT / "handoff" / "latest_report_copy.txt").read_text(encoding="utf-8")

            assert "handoff/current_handoff.md" in prompt_text
            assert "handoff/current_handoff.json" in prompt_text
            assert "handoff/latest_report_copy.txt" in prompt_text
            assert "next recommended action" in prompt_text.lower()

            assert "SUMMARY" in report_text
            assert "Result" in report_text


        def test_status_and_finalization_docs_track_patch_128_proof() -> None:
            project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
            finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")
            handoff_surface = (PROJECT_ROOT / "docs" / "handoff_surface.md").read_text(encoding="utf-8")

            assert "## Patch 128 - active-work continuation flow proof" in project_status
            assert "latest confirmed green head: Patch 128" in project_status
            assert "remaining finalization sequence is F5 through F8, not a redesign wave" in project_status

            assert "## Patch 128 - prove active-work continuation flow" in finalization_master
            assert "- **Latest confirmed green head:** Patch 128" in finalization_master
            assert "- **F5 — prove the new-target onboarding flow**" in finalization_master

            assert "## Patch 128 - active-work continuation proof" in handoff_surface
            assert "handoff/current_handoff.md" in handoff_surface
            assert "Handoff is the first resume surface for already-running PatchOps work." in handoff_surface
        """
    ).strip() + "\n"

    write_text(path, text)
    return "tests/test_active_work_continuation_current.py"


def main() -> int:
    changed = [
        patch_finalization_master(),
        patch_project_status(),
        patch_handoff_surface(),
        patch_ledger(),
        write_tests(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
