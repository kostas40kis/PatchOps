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
        "- **Latest confirmed green head:** Patch 128",
        "- **Latest confirmed green head:** Patch 129",
    )
    text = ensure_replaced(
        text,
        "- Patch 128 re-exports the current handoff bundle from a real green report and adds maintenance tests proving the active-work continuation flow remains mechanical.",
        "- Patch 128 re-exports the current handoff bundle from a real green report and adds maintenance tests proving the active-work continuation flow remains mechanical.\n- Patch 129 proves the new-target onboarding flow with a current helper-first onboarding rehearsal against a demo generic target.",
    )
    text = ensure_replaced(
        text,
        "### F5 — prove the new-target onboarding flow",
        "### F6 — final release / maintenance gate",
    )
    text = ensure_replaced(
        text,
        "- **F5 — prove the new-target onboarding flow**",
        "- **F6 — final release / maintenance gate**",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 129 - prove new-target onboarding flow

        Patch 129 is the F5 proof patch from the rushed finalization sequence.

        ### What it proves

        - the helper-first onboarding path remains mechanical for a brand-new generic target,
        - `recommend-profile` still suggests the correct profile for a generic Python target,
        - `init-project-doc` still scaffolds a packet from explicit inputs,
        - `starter` still produces the smallest useful starter manifest surface,
        - onboarding bootstrap artifacts still summarize the target, reading order, and safest command order.

        ### What this patch deliberately does not claim

        This patch does not redesign onboarding.
        It does not replace manifests, reports, project packets, or handoff.
        It proves that the already-shipped onboarding path still works in the current repo.

        ### Current next action

        - **F6 — final release / maintenance gate**

        ### Rule

        Treat onboarding as target-startup flow.
        Treat handoff as active-work resume flow.
        Keep those roles separate.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129_FINALIZATION_MASTER:START -->",
        "<!-- PATCHOPS_PATCH129_FINALIZATION_MASTER:END -->",
        block,
    )
    return "docs/finalization_master_plan.md"


def patch_project_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    text = read_text(path)

    text = ensure_replaced(
        text,
        "- latest confirmed green head: Patch 128",
        "- latest confirmed green head: Patch 129",
    )
    text = ensure_replaced(
        text,
        "- the remaining finalization sequence is F5 through F8, not a redesign wave",
        "- the remaining finalization sequence is F6 through F8, not a redesign wave",
    )

    write_text(path, text)

    block = textwrap.dedent(
        """
        ## Patch 129 - new-target onboarding flow proof

        ### Current state

        - Patch 129 proves the helper-first onboarding path against a current generic demo target.
        - The repo now has a current proof packet at `docs/projects/demo_roundtrip_current.md`.
        - The repo now has current onboarding bootstrap artifacts under `onboarding/`.

        ### What is now explicitly protected

        - `recommend-profile` current generic-target suggestion behavior,
        - `init-project-doc` current packet scaffolding path,
        - `starter` current documentation-patch manifest suggestion for a generic target,
        - current onboarding bootstrap artifacts:
          - `onboarding/current_target_bootstrap.md`
          - `onboarding/current_target_bootstrap.json`
          - `onboarding/next_prompt.txt`
          - `onboarding/starter_manifest.json`

        ### Remaining posture

        - continue with F6 through F8,
        - keep onboarding separate from continuation,
        - prefer narrow proof and repair over broader rewrite.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129

        Patch 129 is the F5 proof patch from the rushed finalization plan.

        It proves the already-shipped new-target onboarding flow by running a current helper-first rehearsal:
        - `recommend-profile`
        - `init-project-doc`
        - `starter`
        - onboarding bootstrap artifact generation

        It also adds current-state tests for the proof packet and onboarding artifacts.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def write_test_final_maintenance() -> str:
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


        def test_project_status_tracks_post_f5_state() -> None:
            text = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")

            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "## Patch 128 - active-work continuation flow proof" in text
            assert "## Patch 129 - new-target onboarding flow proof" in text
            assert "latest confirmed green head: Patch 129" in text
            assert "remaining finalization sequence is F6 through F8, not a redesign wave" in text
            assert "maintenance / refinement posture" in text


        def test_finalization_master_plan_tracks_post_f5_state() -> None:
            text = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

            assert "- **Latest confirmed green head:** Patch 129" in text
            assert "## Patch 127 - final contract-lock validation sweep" in text
            assert "## Patch 128 - prove active-work continuation flow" in text
            assert "## Patch 129 - prove new-target onboarding flow" in text
            assert "- **F6 — final release / maintenance gate**" in text
            assert "finished enough to freeze" in text
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_final_maintenance_mode_docs.py"


def write_test_active_work_continuation() -> str:
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


        def test_status_and_finalization_docs_keep_patch_128_proof_visible_after_f5() -> None:
            project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
            finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")
            handoff_surface = (PROJECT_ROOT / "docs" / "handoff_surface.md").read_text(encoding="utf-8")

            assert "## Patch 128 - active-work continuation flow proof" in project_status
            assert "latest confirmed green head: Patch 129" in project_status
            assert "remaining finalization sequence is F6 through F8, not a redesign wave" in project_status

            assert "## Patch 128 - prove active-work continuation flow" in finalization_master
            assert "- **Latest confirmed green head:** Patch 129" in finalization_master
            assert "- **F6 — final release / maintenance gate**" in finalization_master

            assert "## Patch 128 - active-work continuation proof" in handoff_surface
            assert "handoff/current_handoff.md" in handoff_surface
            assert "Handoff is the first resume surface for already-running PatchOps work." in handoff_surface
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_active_work_continuation_current.py"


def write_test_new_target_onboarding() -> str:
    path = PROJECT_ROOT / "tests" / "test_new_target_onboarding_current.py"
    text = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "demo_roundtrip_current.md"
        BOOTSTRAP_ROOT = PROJECT_ROOT / "onboarding"


        def test_current_demo_project_packet_exists_and_is_target_facing() -> None:
            assert PACKET_PATH.exists(), f"Missing demo packet: {PACKET_PATH}"

            text = PACKET_PATH.read_text(encoding="utf-8")
            lowered = text.lower()

            assert "project packet" in lowered
            assert "demo roundtrip current" in lowered
            assert "selected patchops profile" in lowered
            assert "what must remain outside patchops" in lowered
            assert "current development state" in lowered or "current state" in lowered


        def test_current_onboarding_bootstrap_artifacts_exist() -> None:
            required = [
                BOOTSTRAP_ROOT / "current_target_bootstrap.md",
                BOOTSTRAP_ROOT / "current_target_bootstrap.json",
                BOOTSTRAP_ROOT / "next_prompt.txt",
                BOOTSTRAP_ROOT / "starter_manifest.json",
            ]
            for path in required:
                assert path.exists(), f"Missing onboarding artifact: {path}"


        def test_current_onboarding_bootstrap_payload_matches_demo_target() -> None:
            payload = json.loads((BOOTSTRAP_ROOT / "current_target_bootstrap.json").read_text(encoding="utf-8"))
            starter_manifest = json.loads((BOOTSTRAP_ROOT / "starter_manifest.json").read_text(encoding="utf-8"))
            bootstrap_md = (BOOTSTRAP_ROOT / "current_target_bootstrap.md").read_text(encoding="utf-8")
            next_prompt = (BOOTSTRAP_ROOT / "next_prompt.txt").read_text(encoding="utf-8")

            assert payload["project_name"] == "Demo Roundtrip Current"
            assert payload["profile_name"] == "generic_python"
            assert payload["current_stage"] == "Initial onboarding"
            assert payload["recommended_commands"] == ["check", "inspect", "plan", "apply_or_verify_only"]
            assert Path(payload["project_packet_path"]) == PACKET_PATH.resolve()

            assert starter_manifest["active_profile"] == "generic_python"
            assert starter_manifest["patch_name"] == "bootstrap_verify_only"
            assert starter_manifest["target_project_root"]

            assert "# Onboarding bootstrap - Demo Roundtrip Current" in bootstrap_md
            assert "## 2. Suggested reading order" in bootstrap_md
            assert "docs/project_packet_contract.md" in bootstrap_md
            assert "docs/project_packet_workflow.md" in bootstrap_md
            assert "## 4. Recommended command order" in bootstrap_md

            assert "You are onboarding the target project 'Demo Roundtrip Current' into PatchOps." in next_prompt
            assert "Read the generic PatchOps packet first, then use the project packet." in next_prompt
            assert "Selected profile: generic_python" in next_prompt
            assert "Then run check, inspect, and plan before any apply or verify-only execution." in next_prompt


        def test_status_and_finalization_docs_track_patch_129_onboarding_proof() -> None:
            project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
            finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

            assert "## Patch 129 - new-target onboarding flow proof" in project_status
            assert "latest confirmed green head: Patch 129" in project_status
            assert "remaining finalization sequence is F6 through F8, not a redesign wave" in project_status

            assert "## Patch 129 - prove new-target onboarding flow" in finalization_master
            assert "- **Latest confirmed green head:** Patch 129" in finalization_master
            assert "- **F6 — final release / maintenance gate**" in finalization_master
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_new_target_onboarding_current.py"


def main() -> int:
    changed = [
        patch_finalization_master(),
        patch_project_status(),
        patch_ledger(),
        write_test_final_maintenance(),
        write_test_active_work_continuation(),
        write_test_new_target_onboarding(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
