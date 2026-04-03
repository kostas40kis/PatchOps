from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

wrapper_root = Path(sys.argv[1]).resolve()
manifest_path = Path(sys.argv[2]).resolve()
patch_name = "patch_131_final_documentation_stop_history_compression"
latest_gate_report = r"C:\Users\kostas\Desktop\patch_130_final_release_maintenance_gate_patch_130_final_release_maintenance_gate_20260328_202245.txt"
python_exe = sys.executable

DOC_PATHS = (
    "README.md",
    "docs/project_status.md",
    "docs/llm_usage.md",
    "docs/operator_quickstart.md",
    "docs/examples.md",
    "docs/handoff_surface.md",
    "docs/project_packet_workflow.md",
    "docs/project_packet_contract.md",
    "docs/patch_ledger.md",
    "docs/finalization_master_plan.md",
)

def read_text_or_default(path: Path, default: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default

def append_unique_block(existing: str, block: str, marker: str) -> str:
    if marker in existing:
        return existing
    base = existing.rstrip()
    if base:
        return base + "\n\n" + block.strip() + "\n"
    return block.strip() + "\n"

doc_blocks = {
    "README.md": dedent(f"""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_README:START -->
    ## Final maintained reading order

    PatchOps is now in maintenance mode after the final release / maintenance gate passed in Patch 130.

    ### Start here for already-running PatchOps work

    1. read `handoff/current_handoff.md`
    2. read `handoff/current_handoff.json`
    3. read `handoff/latest_report_copy.txt`
    4. then read `docs/project_status.md`
    5. then read `docs/llm_usage.md`

    ### Start here for a brand-new target project

    1. read `README.md`
    2. read `docs/llm_usage.md`
    3. read `docs/operator_quickstart.md`
    4. read `docs/project_packet_contract.md`
    5. read `docs/project_packet_workflow.md`
    6. then read or create the relevant file under `docs/projects/`

    ### History-compression reminder

    Treat the following as the final maintained reading set rather than reconstructing state from old chat history:

    - `README.md`
    - `docs/project_status.md`
    - `docs/llm_usage.md`
    - `docs/operator_quickstart.md`
    - `docs/examples.md`
    - `docs/handoff_surface.md`
    - `docs/project_packet_workflow.md`
    - `docs/project_packet_contract.md`
    - `docs/patch_ledger.md`
    - `docs/finalization_master_plan.md`

    ### Scope reminder

    - historical anchors explain how the repo got here,
    - shipped behavior is the truth to operate from now,
    - optional future work is additive only,
    - target-specific extension work belongs in target packets, profiles, manifests, and target repos rather than inside generic PatchOps core logic.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_README:END -->
    """).strip(),
    "docs/project_status.md": dedent(f"""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_STATUS:START -->
    ## Patch 131 - final documentation stop and history compression

    Patch 131 is the final documentation stop after Patch 130 passed the release / maintenance gate.

    Latest trusted gate report:
    `{latest_gate_report}`

    ### Shipped behavior

    PatchOps should now be treated as:

    - finished as an initial product,
    - in maintenance mode,
    - mechanically usable for active-work continuation,
    - mechanically usable for brand-new target onboarding,
    - protected by maintained operator, handoff, onboarding, and validation surfaces.

    ### Historical anchors

    Historical plans, older freeze-point prompts, and earlier patch narratives remain useful as anchors.
    They do not override current repo files, current tests, current handoff artifacts, or the latest successful validation reports.

    ### Optional future work

    Optional future work is additive only.
    It may extend target coverage, helpers, or export ergonomics without reopening the core architecture.

    ### Target-specific extension work

    Target-specific extension work belongs in:

    - target repos,
    - target project packets under `docs/projects/`,
    - target-aligned manifests,
    - target profiles where executable assumptions are needed.

    It does not belong in the generic PatchOps core unless the behavior is truly reusable.

    ### Reading-order rule after chat-history loss

    If earlier chat history disappears, the minimum durable reading order is:

    1. `handoff/current_handoff.md` for already-running work, or the generic docs for brand-new target onboarding,
    2. `docs/project_status.md`,
    3. `docs/llm_usage.md`,
    4. `docs/operator_quickstart.md`,
    5. `docs/examples.md`,
    6. `docs/patch_ledger.md`,
    7. `docs/finalization_master_plan.md`.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_STATUS:END -->
    """).strip(),
    "docs/llm_usage.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START -->
    ## Final start-here guide after history compression

    Use the smallest correct reading path.

    ### If PatchOps work is already in progress

    Start with the handoff bundle:

    1. `handoff/current_handoff.md`
    2. `handoff/current_handoff.json`
    3. `handoff/latest_report_copy.txt`

    Then read:

    4. `docs/project_status.md`
    5. `docs/operator_quickstart.md`
    6. `docs/examples.md`

    ### If you are starting a brand-new target project

    Start with the generic onboarding packet:

    1. `README.md`
    2. `docs/llm_usage.md`
    3. `docs/operator_quickstart.md`
    4. `docs/project_packet_contract.md`
    5. `docs/project_packet_workflow.md`

    Then read or create the relevant file under `docs/projects/`.

    ### Boundary rules

    - use handoff for already-running PatchOps work,
    - use the generic packet plus a project packet for brand-new target work,
    - use manifests to tell PatchOps what to do now,
    - use reports to prove what happened,
    - do not treat old chat history as the primary state source once these maintained docs exist.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:END -->
    """).strip(),
    "docs/operator_quickstart.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START -->
    ## Final quickstart split

    Choose the path that matches reality.

    ### Path A - continue already-running PatchOps work

    - read `handoff/current_handoff.md`
    - read `handoff/current_handoff.json`
    - read `handoff/latest_report_copy.txt`
    - follow the exact next recommended action from the handoff
    - use `docs/examples.md` only if a new manifest must still be authored

    ### Path B - start a brand-new target project

    - read the generic PatchOps packet
    - read `docs/project_packet_contract.md`
    - read `docs/project_packet_workflow.md`
    - read or create the relevant file under `docs/projects/`
    - choose the smallest correct example or starter helper
    - continue with normal manifest-driven work

    ### Final reminder

    The repo is in maintenance mode.
    Prefer narrow repair, narrow refresh, and explicit evidence over broad redesign.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:END -->
    """).strip(),
    "docs/examples.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START -->
    ## Final example selection guidance

    Use examples mechanically instead of starting from a blank page when one of these already matches the work.

    ### For already-running PatchOps continuation

    - use the handoff bundle first,
    - then choose the smallest matching example only if a new manifest must be authored.

    ### For brand-new generic target work

    Lowest-friction generic starts:

    - `examples/generic_python_patch.json`
    - `examples/generic_verify_patch.json`
    - `examples/generic_python_powershell_patch.json`
    - `examples/generic_python_powershell_verify_patch.json`

    ### For conservative trader-target starts

    Lowest-friction trader starts:

    - `examples/trader_first_doc_patch.json`
    - `examples/trader_first_verify_patch.json`

    Broader trader examples:

    - `examples/trader_doc_patch.json`
    - `examples/trader_verify_patch.json`
    - `examples/trader_code_patch.json`

    ### Boundary reminder

    Examples are starter surfaces.
    They do not replace project packets, handoff files, manifests, or canonical reports.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:END -->
    """).strip(),
    "docs/handoff_surface.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:START -->
    ## Final handoff boundary note

    The handoff bundle is the maintained continuation surface for already-running PatchOps work.

    Read these first for continuation:

    - `handoff/current_handoff.md`
    - `handoff/current_handoff.json`
    - `handoff/latest_report_copy.txt`

    The handoff bundle does not replace:

    - project packets for target onboarding,
    - manifests for current execution intent,
    - canonical reports for run evidence,
    - current repo files and tests as the highest-priority truth source.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:END -->
    """).strip(),
    "docs/project_packet_workflow.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START -->
    ## Final onboarding-versus-continuation rule

    Use the project-packet workflow only for brand-new target projects.

    ### Brand-new target onboarding

    1. read the generic PatchOps packet,
    2. read `docs/project_packet_contract.md`,
    3. read `docs/project_packet_workflow.md`,
    4. read or create the relevant file under `docs/projects/`,
    5. choose a starter helper, template, or example,
    6. continue with normal manifest-driven PatchOps work.

    ### Already-running PatchOps continuation

    Do not start from project-packet onboarding when the work is already in progress.
    Start from the handoff bundle instead and let the handoff define the next action.

    ### Final boundary reminder

    - generic docs teach PatchOps,
    - project packets teach one target project,
    - manifests tell PatchOps what to do now,
    - reports prove what happened,
    - handoff files tell the next LLM how to continue from the latest run.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:END -->
    """).strip(),
    "docs/project_packet_contract.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START -->
    ## Final project-packet contract reminder

    A project packet is the maintained target-facing contract inside PatchOps.

    ### Stable layer

    The stable layer should explain:

    - what the target project is,
    - expected roots,
    - expected runtime,
    - selected profile,
    - what must remain outside PatchOps,
    - recommended examples and starter posture.

    ### Mutable layer

    The mutable layer should explain:

    - current phase,
    - current objective,
    - latest passed patch,
    - latest attempted patch,
    - blockers,
    - next recommended action.

    ### Boundary reminder

    A project packet does not replace:

    - profiles,
    - manifests,
    - reports,
    - handoff files.

    It complements them by making target onboarding faster and less interpretive.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:END -->
    """).strip(),
    "docs/patch_ledger.md": dedent("""
    ## Patch 131

    Patch 131 is the final documentation stop and history-compression patch.

    It refreshes the final maintained reading set, adds explicit start-here guidance for both continuation and brand-new target onboarding, and makes the doc boundaries between historical anchors, shipped behavior, optional future work, and target-specific extension work easier to read after chat-history loss.

    This patch is a documentation stop, not a redesign patch.
    """).strip(),
    "docs/finalization_master_plan.md": dedent("""
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:START -->
    ## F7 completion note

    F6 has already passed.
    F7 is the final documentation stop and history-compression pass.

    After this doc stop, the maintained reading order should be treated as:

    1. handoff bundle first for already-running work,
    2. generic packet plus project packet for brand-new target onboarding,
    3. project status, operator quickstart, examples, patch ledger, and this finalization plan as the durable repo-level orientation set.

    The purpose of this step is not to redesign PatchOps again.
    Its purpose is to make the repo readable and mechanically usable even if earlier chat history disappears.
    <!-- PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:END -->
    """).strip(),
}

defaults = {
    "README.md": "# PatchOps\n",
    "docs/project_status.md": "# PatchOps project status\n",
    "docs/llm_usage.md": "# PatchOps LLM usage\n",
    "docs/operator_quickstart.md": "# PatchOps operator quickstart\n",
    "docs/examples.md": "# PatchOps examples\n",
    "docs/handoff_surface.md": "# PatchOps handoff surface\n",
    "docs/project_packet_workflow.md": "# PatchOps project packet workflow\n",
    "docs/project_packet_contract.md": "# PatchOps project packet contract\n",
    "docs/patch_ledger.md": "# PatchOps patch ledger\n",
    "docs/finalization_master_plan.md": "# PatchOps finalization master plan\n",
}

doc_markers = {
    "README.md": "PATCHOPS_F7_FINAL_DOC_STOP_README:START",
    "docs/project_status.md": "PATCHOPS_F7_FINAL_DOC_STOP_STATUS:START",
    "docs/llm_usage.md": "PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START",
    "docs/operator_quickstart.md": "PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START",
    "docs/examples.md": "PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START",
    "docs/handoff_surface.md": "PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:START",
    "docs/project_packet_workflow.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START",
    "docs/project_packet_contract.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START",
    "docs/patch_ledger.md": "## Patch 131",
    "docs/finalization_master_plan.md": "PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:START",
}

updated_docs = {}
for relative_path in DOC_PATHS:
    path = wrapper_root / relative_path
    current_text = read_text_or_default(path, defaults[relative_path])
    updated_docs[relative_path] = append_unique_block(
        current_text,
        doc_blocks[relative_path],
        doc_markers[relative_path],
    )

test_text = dedent("""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOC_MARKERS = {
    "README.md": "PATCHOPS_F7_FINAL_DOC_STOP_README:START",
    "docs/project_status.md": "PATCHOPS_F7_FINAL_DOC_STOP_STATUS:START",
    "docs/llm_usage.md": "PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START",
    "docs/operator_quickstart.md": "PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START",
    "docs/examples.md": "PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START",
    "docs/handoff_surface.md": "PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:START",
    "docs/project_packet_workflow.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START",
    "docs/project_packet_contract.md": "PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START",
    "docs/finalization_master_plan.md": "PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:START",
}

def test_f7_doc_stop_markers_exist() -> None:
    for relative_path, marker in DOC_MARKERS.items():
        text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert marker in text, f"missing F7 marker in {relative_path}"

def test_f7_reading_order_and_boundary_language_is_present() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8").lower()
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    operator = (PROJECT_ROOT / "docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    project_status = (PROJECT_ROOT / "docs/project_status.md").read_text(encoding="utf-8").lower()
    packet_workflow = (PROJECT_ROOT / "docs/project_packet_workflow.md").read_text(encoding="utf-8").lower()
    packet_contract = (PROJECT_ROOT / "docs/project_packet_contract.md").read_text(encoding="utf-8").lower()
    handoff_surface = (PROJECT_ROOT / "docs/handoff_surface.md").read_text(encoding="utf-8").lower()
    examples = (PROJECT_ROOT / "docs/examples.md").read_text(encoding="utf-8").lower()
    patch_ledger = (PROJECT_ROOT / "docs/patch_ledger.md").read_text(encoding="utf-8").lower()
    finalization_plan = (PROJECT_ROOT / "docs/finalization_master_plan.md").read_text(encoding="utf-8").lower()

    assert "handoff/current_handoff.md" in readme
    assert "brand-new target project" in readme
    assert "historical anchors" in readme
    assert "target-specific extension work" in readme

    assert "generic onboarding packet" in llm_usage
    assert "handoff/current_handoff.json" in llm_usage

    assert "path a - continue already-running patchops work" in operator
    assert "path b - start a brand-new target project" in operator

    assert "finished as an initial product" in project_status
    assert "optional future work" in project_status
    assert "target-specific extension work" in project_status

    assert "use the project-packet workflow only for brand-new target projects" in packet_workflow
    assert "start from the handoff bundle instead" in packet_workflow

    assert "stable layer" in packet_contract
    assert "mutable layer" in packet_contract
    assert "does not replace" in packet_contract

    assert "maintained continuation surface for already-running patchops work" in handoff_surface
    assert "does not replace" in handoff_surface

    assert "generic_python_powershell_patch.json" in examples
    assert "trader_first_verify_patch.json" in examples

    assert "## patch 131" in patch_ledger
    assert "history-compression patch" in patch_ledger

    assert "f6 has already passed" in finalization_plan
    assert "history disappears" in finalization_plan

def test_f7_final_docs_preserve_start_here_distinction() -> None:
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    operator = (PROJECT_ROOT / "docs/operator_quickstart.md").read_text(encoding="utf-8").lower()

    assert "if patchops work is already in progress" in llm_usage
    assert "if you are starting a brand-new target project" in llm_usage
    assert "already-running patchops work" in operator
    assert "brand-new target project" in operator
""").strip() + "\n"

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python_powershell",
    "target_project_root": str(wrapper_root).replace("\\", "/"),
    "backup_files": list(DOC_PATHS) + ["tests/test_final_documentation_stop_history_compression.py"],
    "files_to_write": [
        {
            "path": relative_path,
            "content": updated_docs[relative_path],
            "content_path": None,
            "encoding": "utf-8",
        }
        for relative_path in DOC_PATHS
    ] + [
        {
            "path": "tests/test_final_documentation_stop_history_compression.py",
            "content": test_text,
            "content_path": None,
            "encoding": "utf-8",
        }
    ],
    "validation_commands": [
        {
            "name": "full_pytest",
            "program": python_exe,
            "args": ["-m", "pytest", "-q"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
        {
            "name": "release_readiness",
            "program": python_exe,
            "args": [
                "-m",
                "patchops.cli",
                "release-readiness",
                "--wrapper-root",
                ".",
                "--profile",
                "generic_python_powershell",
                "--core-tests-green",
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
    ],
    "smoke_commands": [],
    "audit_commands": [
        {
            "name": "profiles_summary",
            "program": python_exe,
            "args": ["-m", "patchops.cli", "profiles", "--wrapper-root", "."],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
        {
            "name": "examples_index",
            "program": python_exe,
            "args": ["-m", "patchops.cli", "examples"],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        },
    ],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": None,
        "report_name_prefix": patch_name,
        "write_to_desktop": True,
    },
    "tags": [
        "finalization",
        "f7",
        "documentation_stop",
        "history_compression",
        "self_hosted",
    ],
    "notes": "F7 final documentation stop and history-compression patch for PatchOps self-hosted finalization.",
}

manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(str(manifest_path))