from __future__ import annotations

import textwrap
from pathlib import Path

PROJECT_ROOT = Path(r"C:\dev\patchops")
TEST_PATH = PROJECT_ROOT / "tests" / "test_onboarding_bootstrap_artifacts_current.py"
PATCH_LEDGER_PATH = PROJECT_ROOT / "docs" / "patch_ledger.md"
PROJECT_STATUS_PATH = PROJECT_ROOT / "docs" / "project_status.md"


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


test_content = textwrap.dedent(
    """\
    from __future__ import annotations

    import json
    from pathlib import Path

    from patchops.project_packets import build_onboarding_bootstrap


    def test_onboarding_bootstrap_artifacts_match_current_contract(tmp_path: Path) -> None:
        payload = build_onboarding_bootstrap(
            project_name="Demo Bootstrap",
            target_root=r"C:\\dev\\demo_bootstrap",
            profile_name="generic_python",
            wrapper_project_root=tmp_path,
            runtime_path=r"C:\\dev\\demo_bootstrap\\.venv\\Scripts\\python.exe",
            initial_goals=["Create the first packet", "Generate the safest starter manifest"],
            current_stage="Initial onboarding",
        )

        onboarding_root = tmp_path / "onboarding"
        bootstrap_md = onboarding_root / "current_target_bootstrap.md"
        bootstrap_json = onboarding_root / "current_target_bootstrap.json"
        next_prompt = onboarding_root / "next_prompt.txt"
        starter_manifest = onboarding_root / "starter_manifest.json"

        assert bootstrap_md.exists()
        assert bootstrap_json.exists()
        assert next_prompt.exists()
        assert starter_manifest.exists()

        md_text = bootstrap_md.read_text(encoding="utf-8")
        assert "# Onboarding bootstrap - Demo Bootstrap" in md_text
        assert "## 1. Identity" in md_text
        assert "- **Project name:** Demo Bootstrap" in md_text
        assert "- **Target root:** `C:\\\\dev\\\\demo_bootstrap`" in md_text
        assert "- **Profile:** `generic_python`" in md_text
        assert "## 2. Suggested reading order" in md_text
        assert "README.md" in md_text
        assert "docs/llm_usage.md" in md_text
        assert "docs/project_packet_contract.md" in md_text
        assert "docs/project_packet_workflow.md" in md_text
        assert "## 4. Recommended command order" in md_text
        assert "1. check" in md_text
        assert "2. inspect" in md_text
        assert "3. plan" in md_text
        assert "4. apply or verify-only" in md_text

        json_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
        assert json_payload["project_name"] == "Demo Bootstrap"
        assert json_payload["target_root"] == r"C:\\dev\\demo_bootstrap"
        assert json_payload["profile_name"] == "generic_python"
        assert json_payload["current_stage"] == "Initial onboarding"
        assert json_payload["initial_goals"] == ["Create the first packet", "Generate the safest starter manifest"]
        assert json_payload["recommended_commands"] == ["check", "inspect", "plan", "apply_or_verify_only"]
        assert Path(json_payload["bootstrap_markdown_path"]) == bootstrap_md.resolve()
        assert Path(json_payload["starter_manifest_path"]) == starter_manifest.resolve()
        assert Path(json_payload["next_prompt_path"]) == next_prompt.resolve()

        prompt_text = next_prompt.read_text(encoding="utf-8")
        assert "You are onboarding the target project 'Demo Bootstrap' into PatchOps." in prompt_text
        assert "Read the generic PatchOps packet first, then use the project packet." in prompt_text
        assert "Selected profile: generic_python" in prompt_text
        assert "Target root: C:\\\\dev\\\\demo_bootstrap" in prompt_text
        assert "Restate what PatchOps owns, what remains outside PatchOps, and the safest first manifest shape." in prompt_text
        assert "Then run check, inspect, and plan before any apply or verify-only execution." in prompt_text

        manifest_payload = json.loads(starter_manifest.read_text(encoding="utf-8"))
        assert manifest_payload["manifest_version"] == "1"
        assert manifest_payload["patch_name"] == "bootstrap_verify_only"
        assert manifest_payload["active_profile"] == "generic_python"
        assert manifest_payload["target_project_root"] == "C:/dev/demo_bootstrap"
        assert manifest_payload["files_to_write"] == []
        assert manifest_payload["validation_commands"] == []
        assert "Generated by bootstrap-target." in manifest_payload["notes"]

        assert payload["project_name"] == "Demo Bootstrap"
        assert payload["profile_name"] == "generic_python"
        assert Path(payload["bootstrap_markdown_path"]) == bootstrap_md.resolve()
        assert Path(payload["starter_manifest_path"]) == starter_manifest.resolve()
    """
)

ledger_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94_LEDGER:START -->
    ## Patch 94

    Patch 94 adds a maintenance validation surface for the actual onboarding bootstrap artifacts.

    It proves that the generated bootstrap markdown, JSON payload, next prompt, and starter manifest still match the current contract already described by the onboarding docs and current project-packet rollout.

    This is a narrow validation patch, not an onboarding redesign.
    <!-- PATCHOPS_PATCH94_LEDGER:END -->
    """
)

status_block = textwrap.dedent(
    """\
    <!-- PATCHOPS_PATCH94_STATUS:START -->
    ## Patch 94 - onboarding bootstrap artifact contract validation

    ### Current state

    - Patch 94 adds a direct contract test for the actual onboarding bootstrap outputs.
    - The new test proves the current artifact set remains stable:
      - `current_target_bootstrap.md`,
      - `current_target_bootstrap.json`,
      - `next_prompt.txt`,
      - `starter_manifest.json`.

    ### Why this matters

    - the repo now protects the generated onboarding artifacts themselves, not only the docs around them,
    - the faster first-use onboarding surface stays grounded in a concrete test,
    - the onboarding layer remains in maintenance/refinement posture.

    ### Remaining posture

    - continue with narrow maintenance, refinement, or target-specific expansion,
    - prefer small validation patches when the feature already exists and the main risk is contract drift.
    <!-- PATCHOPS_PATCH94_STATUS:END -->
    """
)

ensure_parent(TEST_PATH)
TEST_PATH.write_text(test_content, encoding="utf-8")

upsert_block(
    PATCH_LEDGER_PATH,
    "<!-- PATCHOPS_PATCH94_LEDGER:START -->",
    "<!-- PATCHOPS_PATCH94_LEDGER:END -->",
    ledger_block,
)

upsert_block(
    PROJECT_STATUS_PATH,
    "<!-- PATCHOPS_PATCH94_STATUS:START -->",
    "<!-- PATCHOPS_PATCH94_STATUS:END -->",
    status_block,
)

print(f"WROTE: {TEST_PATH}")
print(f"UPDATED: {PATCH_LEDGER_PATH}")
print(f"UPDATED: {PROJECT_STATUS_PATH}")