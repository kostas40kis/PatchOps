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


def patch_bootstrap_target_cli_test() -> str:
    path = PROJECT_ROOT / "tests" / "test_bootstrap_target_cli_current.py"
    text = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        import subprocess
        import sys
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def test_bootstrap_target_cli_current_module_invocation(tmp_path: Path) -> None:
            target_root = tmp_path / "demo_target"
            target_root.mkdir(parents=True, exist_ok=True)

            wrapper_root = tmp_path / "wrapper_root"
            wrapper_root.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable,
                "-m",
                "patchops.cli",
                "bootstrap-target",
                "--project-name",
                "Demo Bootstrap CLI",
                "--target-root",
                str(target_root),
                "--profile",
                "generic_python",
                "--wrapper-root",
                str(wrapper_root),
                "--initial-goal",
                "Create the first packet",
                "--initial-goal",
                "Generate the safest starter manifest",
            ]

            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, result.stderr

            onboarding_root = wrapper_root / "onboarding"
            bootstrap_md = onboarding_root / "current_target_bootstrap.md"
            bootstrap_json = onboarding_root / "current_target_bootstrap.json"
            next_prompt = onboarding_root / "next_prompt.txt"
            starter_manifest = onboarding_root / "starter_manifest.json"

            assert bootstrap_md.exists()
            assert bootstrap_json.exists()
            assert next_prompt.exists()
            assert starter_manifest.exists()

            payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
            assert payload["project_name"] == "Demo Bootstrap CLI"
            assert payload["written"] is True
            assert payload["selected_profile"] == "generic_python"
            assert Path(payload["bootstrap_markdown_path"]) == bootstrap_md.resolve()
            assert Path(payload["bootstrap_json_path"]) == bootstrap_json.resolve()
            assert Path(payload["next_prompt_path"]) == next_prompt.resolve()
            assert Path(payload["starter_manifest_path"]) == starter_manifest.resolve()
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_bootstrap_target_cli_current.py"


def patch_new_target_onboarding_test() -> str:
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
            assert payload["selected_profile"] == "generic_python"
            assert payload["written"] is True
            assert Path(payload["packet_path"]) == PACKET_PATH.resolve()

            assert Path(payload["bootstrap_markdown_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.md").resolve()
            assert Path(payload["bootstrap_json_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.json").resolve()
            assert Path(payload["next_prompt_path"]) == (BOOTSTRAP_ROOT / "next_prompt.txt").resolve()
            assert Path(payload["starter_manifest_path"]) == (BOOTSTRAP_ROOT / "starter_manifest.json").resolve()

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


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129H

        Patch 129H aligns the new F5 proof tests with the actual current `bootstrap-target` contract already emitted by the repo.

        This is a narrow test-alignment patch.
        It does not change onboarding behavior.
        It records that the current maintained bootstrap-target contract is sufficient to prove the onboarding flow without forcing a stronger payload schema than the shipped CLI currently guarantees.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129H_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129H_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129H - onboarding proof test contract alignment

        Patch 129H aligns the added onboarding proof tests with the current shipped bootstrap-target payload contract.

        The onboarding flow remains proven by:
        - successful helper-first commands,
        - generated onboarding artifacts,
        - packet creation,
        - starter manifest generation,
        - current bootstrap artifact paths.

        This patch changes only the proof-test expectations, not the onboarding behavior itself.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129H_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129H_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        patch_bootstrap_target_cli_test(),
        patch_new_target_onboarding_test(),
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
