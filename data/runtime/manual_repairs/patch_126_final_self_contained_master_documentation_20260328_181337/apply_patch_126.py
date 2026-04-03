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
    if path.exists():
        text = read_text(path)
    else:
        text = ""

    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL,
    )

    if pattern.search(text):
        updated = pattern.sub(block, text, count=1)
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        updated = text.rstrip() + "\n\n" + block + "\n"

    write_text(path, updated)


def write_finalization_master() -> None:
    path = PROJECT_ROOT / "docs" / "finalization_master_plan.md"
    text = textwrap.dedent(
        """
        # PatchOps Finalization Master Plan

        ## 1. Purpose

        This file is the maintained finalization anchor for PatchOps.
        It is meant to be strong enough that a future LLM can continue the project without prior chat history.

        Its job is to make five things explicit:

        1. what PatchOps is and is not,
        2. what is already shipped,
        3. what posture the repo is in now,
        4. what remains in the rushed finalization sequence,
        5. what must not be redesigned casually.

        This is not a new architecture roadmap.
        It is a maintained finalization and freeze guide.

        ---

        ## 2. Project identity

        - **Project name:** PatchOps
        - **Workspace root:** `C:\\dev`
        - **Wrapper repo root:** `C:\\dev\\patchops`
        - **Example target repo:** `C:\\dev\\trader`
        - **Platform:** Windows + PowerShell + Python launcher (`py -3`)
        - **Design posture:** project-agnostic, manifest-driven, evidence-driven, future-LLM-friendly

        ---

        ## 3. What PatchOps is

        PatchOps is a standalone wrapper / harness / patch-execution toolkit.

        PatchOps owns how change is:

        - planned,
        - applied,
        - validated,
        - evidenced,
        - rerun,
        - handed off,
        - and bootstrapped for brand-new target projects.

        Simple boundary:

        - **PatchOps = how change is applied, validated, evidenced, retried, and handed off**
        - **target repo = what the change actually is**

        ### What PatchOps is not

        PatchOps is not:

        - trader business logic,
        - OSM business logic,
        - target-side strategy/application logic,
        - or a second PowerShell workflow engine.

        ---

        ## 4. Non-negotiable architecture rules

        ### 4.1 Keep PowerShell thin
        PowerShell remains operator-facing and evidence-oriented.

        ### 4.2 Keep reusable logic in Python
        Python continues to own manifests, profile resolution, file operations, reporting helpers, handoff generation, project-packet helpers, onboarding bootstrap generation, and validation logic.

        ### 4.3 Keep the wrapper project-agnostic
        Trader is the first serious maintained target example.
        It is not the identity of the wrapper.

        ### 4.4 Keep one-report evidence discipline
        Each patch flow should still end with one canonical Desktop txt report.

        ### 4.5 Prefer narrow validation and repair over redesign
        The default move in this repo is now:
        - verify reality,
        - repair narrowly,
        - refresh docs,
        - lock drift with tests only when needed.

        ### 4.6 Do not move target-project business logic into PatchOps
        PatchOps must not absorb target-repo domain behavior.

        ---

        ## 5. Current interpreted repo state

        PatchOps should now be interpreted as a **maintenance / refinement** repository rather than a greenfield buildout.

        The truth-reset wave has already happened:

        - Patch 125 identified a narrow blocker,
        - Patch 125A repaired the first wording regressions,
        - Patch 125B repaired the remaining wording regressions and returned the suite to green,
        - Patch 126 refreshes the self-contained documentation set that a future LLM can use without prior chat history.

        ### Latest confirmed green head

        - **Latest confirmed green head:** Patch 126

        ### Shipped layers already present in meaningful form

        1. **Core wrapper engine**
           - manifests,
           - profiles,
           - apply / verify / reporting,
           - deterministic evidence posture.

        2. **Handoff-first continuation**
           - handoff bundle generation surfaces,
           - current-handoff docs orientation,
           - latest-report / next-prompt continuation story.

        3. **Two-step onboarding / project packets**
           - project packet contract and workflow docs,
           - `docs/projects/` target packets,
           - packet initialization / refresh / helper surfaces,
           - onboarding bootstrap artifacts.

        ### Current posture

        The repo should be treated as:

        - finished enough as an initial product,
        - in maintenance-mode finalization,
        - open to narrow validation, proof, and freeze work,
        - not open to casual core redesign.

        ---

        ## 6. What is already done

        The following should now be considered shipped in meaningful form:

        - the manifest-driven wrapper core,
        - profile-driven target resolution,
        - canonical one-report evidence discipline,
        - verify-only and wrapper-only recovery posture,
        - handoff-first continuation,
        - project-packet onboarding for new targets.

        In other words:
        the remaining work is not “build the product.”
        The remaining work is “prove, lock, compress, and freeze the product honestly.”

        ---

        ## 7. How to continue already-running work

        For an already-running PatchOps effort, the continuation path should be mechanical.

        ### Default reading order

        1. `handoff/current_handoff.md`
        2. `handoff/current_handoff.json`
        3. `handoff/latest_report_copy.txt`
        4. `docs/project_status.md`
        5. `docs/patch_ledger.md`

        ### Default behavior

        - restate current state briefly,
        - identify the exact next recommended action,
        - perform only that next action,
        - prefer narrow repair over broad rewrite.

        If the handoff bundle is missing or stale, do not invent state.
        Trust current repo files, current tests, and the latest report over historical prompts.

        ---

        ## 8. How to start a brand-new target project

        For a brand-new target project, the onboarding path should also be mechanical.

        ### Maintained generic packet

        Read these first:

        1. `README.md`
        2. `docs/overview.md`
        3. `docs/llm_usage.md`
        4. `docs/manifest_schema.md`
        5. `docs/profile_system.md`
        6. `docs/compatibility_notes.md`
        7. `docs/failure_repair_guide.md`
        8. `docs/examples.md`
        9. `docs/project_status.md`
        10. `docs/operator_quickstart.md`
        11. `docs/project_packet_contract.md`
        12. `docs/project_packet_workflow.md`

        ### Target-specific step

        Then create or read:

        - `docs/projects/<project_name>.md`

        Then choose the nearest safe example/manifest surface and continue with the normal PatchOps flow:
        - `check`
        - `inspect`
        - `plan`
        - apply or verify
        - read the canonical report
        - refresh the project packet

        ---

        ## 9. Remaining rushed finalization sequence

        After Patch 126, the remaining sequence is:

        ### F3 — final contract-lock validation sweep
        Lock final posture with narrow tests rather than memory.

        ### F4 — prove the active-work continuation flow
        Confirm the handoff path is practically trustworthy, not just documented.

        ### F5 — prove the new-target onboarding flow
        Confirm the two-step onboarding/project-packet path is practically trustworthy.

        ### F6 — final release / maintenance gate
        Use current readiness/release surfaces to produce an explicit maintenance-mode verdict.

        ### F7 — final documentation stop and history compression
        Refresh the final maintained reading set and compress history into durable docs.

        ### F8 — final source bundle / freeze export
        Generate the final future-LLM export bundle plus canonical freeze report.

        ---

        ## 10. What not to redesign

        Do not do the following unless a validation patch proves a real missing surface:

        - do not redesign the manifest model,
        - do not redesign the profile system,
        - do not widen PowerShell into a second workflow engine,
        - do not move target-repo business logic into PatchOps,
        - do not replace handoff with project packets,
        - do not replace project packets with handoff,
        - do not rewrite every doc from scratch when narrow refresh is enough.

        ---

        ## 11. Honest finish line

        PatchOps should be considered finished enough to freeze when:

        - the final docs make the core truth explicit,
        - continuation is mechanical,
        - onboarding is mechanical,
        - the main operator surface is locked by maintenance-grade validation,
        - the repo clearly says it is in maintenance mode,
        - one final future-LLM export bundle exists.

        At that point, the correct posture is:

        - the core wrapper is done,
        - handoff-first continuation is done,
        - two-step onboarding / project packets are done enough for real use,
        - the remaining work is optional future refinement or target-specific expansion,
        - not unresolved core architecture.

        ---

        ## 12. Current next action

        The next patch after this file refresh is:

        - **F3 — final contract-lock validation sweep**

        That patch should be validation-first.
        It should protect the final posture that is already shipped rather than widen the product.

        <!-- PATCHOPS_PATCH126_FINALIZATION_MASTER:END -->
        """
    ).strip() + "\n"
    write_text(path, text)


def main() -> int:
    write_finalization_master()

    readme_block = textwrap.dedent(
        """
        ## Final maintenance posture

        PatchOps should now be treated as a maintained utility rather than an open-ended architecture buildout.

        The core wrapper, handoff-first continuation, and two-step onboarding / project-packet layers are all shipped in meaningful form.
        The remaining work is finalization and maintenance:

        - protect shipped truth with validation,
        - prove the continuation path,
        - prove the onboarding path,
        - run the final release / maintenance gate,
        - compress the final reading set,
        - export the final freeze bundle.

        ### Start here

        For already-running PatchOps work, start with handoff artifacts when they exist:

        - `handoff/current_handoff.md`
        - `handoff/current_handoff.json`
        - `handoff/latest_report_copy.txt`

        For a brand-new target project, start with:

        - `docs/llm_usage.md`
        - `docs/operator_quickstart.md`
        - `docs/project_packet_contract.md`
        - `docs/project_packet_workflow.md`
        - `docs/finalization_master_plan.md`
        - `docs/patch_ledger.md`

        This repo should now be read as a maintenance-mode wrapper, not as a greenfield architecture project.
        """
    ).strip()

    project_status_block = textwrap.dedent(
        """
        ## Patch 126 - final self-contained master documentation

        This patch refreshes the self-contained operator/LLM documentation set after the truth-reset repair wave.

        ### Current interpreted posture

        - latest confirmed green head: Patch 126
        - the truth-reset blocker found by Patch 125 was repaired by Patch 125A and Patch 125B
        - PatchOps is in a maintenance / refinement posture
        - the core wrapper, handoff-first continuation, and two-step onboarding / project-packet layers are already shipped in meaningful form
        - the remaining finalization sequence is F3 through F8, not a redesign wave

        ### What is done

        - the core manifest/profile/reporting wrapper is done enough for real use
        - handoff-first continuation is done enough for real use
        - two-step onboarding / project packets are done enough for real use

        ### What remains

        - final contract-lock validation sweep
        - continuation proof
        - onboarding proof
        - final release / maintenance gate
        - final documentation stop
        - final source-bundle freeze export

        ### Maintenance rule

        Prefer narrow maintenance, validation, and truth-refresh work over broad rewrites.
        """
    ).strip()

    llm_usage_block = textwrap.dedent(
        """
        ## Final maintenance-mode reading order

        For continuing an already-running PatchOps effort:

        1. read `handoff/current_handoff.md`
        2. read `handoff/current_handoff.json`
        3. read `handoff/latest_report_copy.txt`
        4. read `docs/project_status.md`
        5. then do the exact next recommended action

        For starting a brand-new target project with PatchOps:

        1. read `README.md`
        2. read `docs/llm_usage.md`
        3. read `docs/operator_quickstart.md`
        4. read `docs/project_packet_contract.md`
        5. read `docs/project_packet_workflow.md`
        6. create/read `docs/projects/<project_name>.md`
        7. then choose the nearest safe helper / example / manifest surface

        At finalization time, do not redesign what is already shipped.

        The default move is:

        - verify reality,
        - repair narrowly,
        - refresh docs,
        - lock drift with tests only when needed.

        `docs/finalization_master_plan.md` is the maintained finalization anchor when prior chat history is gone.
        """
    ).strip()

    quickstart_block = textwrap.dedent(
        """
        ## Final maintenance-mode quickstart

        ### Already-running PatchOps work

        - Read the handoff bundle first when it exists.
        - Restate current state briefly.
        - Perform the exact next recommended action.
        - Keep PowerShell thin and reusable logic in Python.

        ### Brand-new target onboarding

        - Read the generic PatchOps packet first.
        - Read or create the project packet under `docs/projects/`.
        - Choose the smallest safe example / manifest surface.
        - Run `check`, `inspect`, `plan`, then apply or verify.

        ### Finalization reading anchor

        - `docs/finalization_master_plan.md` is the self-contained freeze/posture document for future LLM takeover without chat history.
        """
    ).strip()

    ledger_block = textwrap.dedent(
        """
        ## Patch 126

        Patch 126 refreshes the final self-contained documentation set that can survive loss of prior chat history.

        It adds or refreshes:

        - `docs/finalization_master_plan.md`
        - `README.md`
        - `docs/project_status.md`
        - `docs/llm_usage.md`
        - `docs/operator_quickstart.md`

        This is an F2 documentation patch.
        It is meant to restate the repo as a maintenance-mode wrapper whose remaining work is finalization, proof, and freeze rather than redesign.
        """
    ).strip()

    upsert_marked_block(
        PROJECT_ROOT / "README.md",
        "<!-- PATCHOPS_PATCH126_README:START -->",
        "<!-- PATCHOPS_PATCH126_README:END -->",
        readme_block,
    )
    upsert_marked_block(
        PROJECT_ROOT / "docs" / "project_status.md",
        "<!-- PATCHOPS_PATCH126_STATUS:START -->",
        "<!-- PATCHOPS_PATCH126_STATUS:END -->",
        project_status_block,
    )
    upsert_marked_block(
        PROJECT_ROOT / "docs" / "llm_usage.md",
        "<!-- PATCHOPS_PATCH126_LLM_USAGE:START -->",
        "<!-- PATCHOPS_PATCH126_LLM_USAGE:END -->",
        llm_usage_block,
    )
    upsert_marked_block(
        PROJECT_ROOT / "docs" / "operator_quickstart.md",
        "<!-- PATCHOPS_PATCH126_QUICKSTART:START -->",
        "<!-- PATCHOPS_PATCH126_QUICKSTART:END -->",
        quickstart_block,
    )
    upsert_marked_block(
        PROJECT_ROOT / "docs" / "patch_ledger.md",
        "<!-- PATCHOPS_PATCH126_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH126_LEDGER:END -->",
        ledger_block,
    )

    changed = [
        "docs/finalization_master_plan.md",
        "README.md",
        "docs/project_status.md",
        "docs/llm_usage.md",
        "docs/operator_quickstart.md",
        "docs/patch_ledger.md",
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
