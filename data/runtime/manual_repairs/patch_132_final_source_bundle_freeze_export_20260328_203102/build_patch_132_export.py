from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from textwrap import dedent

wrapper_root = Path(sys.argv[1]).resolve()
manifest_path = Path(sys.argv[2]).resolve()
patch_name = "patch_132_final_source_bundle_freeze_export"
latest_doc_stop_report = r"C:\Users\kostas\Desktop\patch_131_final_documentation_stop_history_compression_patch_131_final_documentation_stop_history_compression_20260328_202727.txt"
python_exe = sys.executable

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

doc_defaults = {
    "docs/project_status.md": "# PatchOps project status\n",
    "docs/patch_ledger.md": "# PatchOps patch ledger\n",
    "docs/llm_usage.md": "# PatchOps LLM usage\n",
    "docs/handoff_surface.md": "# PatchOps handoff surface\n",
    "docs/finalization_master_plan.md": "# PatchOps finalization master plan\n",
}

doc_blocks = {
    "docs/project_status.md": dedent(f"""
    <!-- PATCHOPS_F8_FREEZE_EXPORT_STATUS:START -->
    ## Patch 132 - final source bundle freeze export

    Patch 132 produces the durable final future-LLM source bundle and should be treated as the preferred history-compression artifact after the F6 gate and F7 documentation stop.

    Latest trusted pre-export report:
    `{latest_doc_stop_report}`

    ### Preferred history-compression artifact

    Use `handoff/final_future_llm_source_bundle.txt` as the preferred upload artifact when chat history is unavailable or when a future LLM needs one durable repo snapshot.

    ### What this bundle includes

    The final bundle is intended to preserve at minimum:

    - current project status,
    - current handoff bundle,
    - latest report copy,
    - patch ledger,
    - master finalization plan,
    - key operator docs,
    - key onboarding docs,
    - current project-packet examples.

    ### Final freeze stance

    PatchOps should now be treated as:

    - finished as an initial product,
    - in maintenance mode,
    - exportable through one durable final source bundle,
    - ready for additive-only future work.
    <!-- PATCHOPS_F8_FREEZE_EXPORT_STATUS:END -->
    """).strip(),
    "docs/patch_ledger.md": dedent("""
    ## Patch 132

    Patch 132 is the final source bundle freeze-export patch.

    It writes `handoff/final_future_llm_source_bundle.txt`, refreshes the maintained docs so that this file is named explicitly as the preferred history-compression artifact, and adds one narrow test that locks the final bundle presence and bundle-language contract.

    This patch is a freeze-export patch, not a redesign patch.
    """).strip(),
    "docs/llm_usage.md": dedent("""
    <!-- PATCHOPS_F8_FREEZE_EXPORT_LLM_USAGE:START -->
    ## Final freeze-export note

    When a future LLM needs one durable upload artifact rather than several repo files, prefer:

    `handoff/final_future_llm_source_bundle.txt`

    Continue to use the handoff bundle for the most recent run-state, but use the final source bundle when you need one larger, durable, history-compressed source artifact.
    <!-- PATCHOPS_F8_FREEZE_EXPORT_LLM_USAGE:END -->
    """).strip(),
    "docs/handoff_surface.md": dedent("""
    <!-- PATCHOPS_F8_FREEZE_EXPORT_HANDOFF:START -->
    ## Final freeze-export artifact note

    The handoff bundle remains the first continuation surface for already-running work.

    The broader history-compression artifact is:

    `handoff/final_future_llm_source_bundle.txt`

    Use the handoff bundle for immediate run-state continuation.
    Use the final source bundle when one durable upload file is preferred.
    <!-- PATCHOPS_F8_FREEZE_EXPORT_HANDOFF:END -->
    """).strip(),
    "docs/finalization_master_plan.md": dedent("""
    <!-- PATCHOPS_F8_FREEZE_EXPORT_FINALIZATION:START -->
    ## F8 completion note

    F8 is the final source bundle / freeze export step.

    The preferred history-compression artifact after this step is:

    `handoff/final_future_llm_source_bundle.txt`

    That file should be treated as the durable future-LLM export bundle when a single upload artifact is preferred.
    <!-- PATCHOPS_F8_FREEZE_EXPORT_FINALIZATION:END -->
    """).strip(),
}

doc_markers = {
    "docs/project_status.md": "PATCHOPS_F8_FREEZE_EXPORT_STATUS:START",
    "docs/patch_ledger.md": "## Patch 132",
    "docs/llm_usage.md": "PATCHOPS_F8_FREEZE_EXPORT_LLM_USAGE:START",
    "docs/handoff_surface.md": "PATCHOPS_F8_FREEZE_EXPORT_HANDOFF:START",
    "docs/finalization_master_plan.md": "PATCHOPS_F8_FREEZE_EXPORT_FINALIZATION:START",
}

updated_docs = {}
for relative_path, block in doc_blocks.items():
    current_text = read_text_or_default(wrapper_root / relative_path, doc_defaults[relative_path])
    updated_docs[relative_path] = append_unique_block(current_text, block, doc_markers[relative_path])

bundle_include_paths = [
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
    "handoff/current_handoff.md",
    "handoff/current_handoff.json",
    "handoff/latest_report_copy.txt",
    "docs/projects/trader.md",
    "docs/projects/wrapper_self_hosted.md",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
    "examples/generic_python_powershell_patch.json",
    "examples/generic_python_powershell_verify_patch.json",
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
]

def get_effective_text(relative_path: str) -> str | None:
    if relative_path in updated_docs:
        return updated_docs[relative_path]
    path = wrapper_root / relative_path
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None

bundle_lines: list[str] = []
bundle_lines.append("=" * 120)
bundle_lines.append("PATCHOPS FINAL FUTURE LLM SOURCE BUNDLE")
bundle_lines.append("=" * 120)
bundle_lines.append("")
bundle_lines.append(f"Generated    : {datetime.now().astimezone().isoformat(timespec='seconds')}")
bundle_lines.append(f"Project Root : {wrapper_root}")
bundle_lines.append("Purpose      : Preferred history-compression artifact for future LLM continuation or onboarding.")
bundle_lines.append("")
bundle_lines.append("Use this file when a single durable upload artifact is preferred.")
bundle_lines.append("For immediate run-state continuation, the handoff bundle still remains the first surface.")
bundle_lines.append("")
bundle_lines.append("=" * 120)
bundle_lines.append("INCLUDED SOURCES")
bundle_lines.append("=" * 120)
bundle_lines.append("")

for relative_path in bundle_include_paths:
    effective_text = get_effective_text(relative_path)
    status = "FOUND" if effective_text is not None else "MISSING"
    bundle_lines.append(f"{status:<7}: {relative_path}")

bundle_lines.append("")
bundle_lines.append("=" * 120)
bundle_lines.append("SOURCE CONTENTS")
bundle_lines.append("=" * 120)

for relative_path in bundle_include_paths:
    effective_text = get_effective_text(relative_path)
    bundle_lines.append("")
    bundle_lines.append("-" * 120)
    bundle_lines.append(relative_path)
    bundle_lines.append("-" * 120)
    bundle_lines.append("")
    if effective_text is None:
        bundle_lines.append("[MISSING]")
    else:
        bundle_lines.append(effective_text.rstrip())

bundle_text = "\n".join(bundle_lines).rstrip() + "\n"

test_text = dedent("""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_f8_final_source_bundle_exists() -> None:
    bundle_path = PROJECT_ROOT / "handoff/final_future_llm_source_bundle.txt"
    assert bundle_path.exists(), "missing final future-LLM source bundle"

def test_f8_final_source_bundle_mentions_preferred_artifact_and_key_surfaces() -> None:
    text = (PROJECT_ROOT / "handoff/final_future_llm_source_bundle.txt").read_text(encoding="utf-8").lower()

    assert "preferred history-compression artifact" in text
    assert "docs/project_status.md" in text
    assert "handoff/current_handoff.md" in text
    assert "handoff/current_handoff.json" in text
    assert "handoff/latest_report_copy.txt" in text
    assert "docs/finalization_master_plan.md" in text
    assert "docs/project_packet_workflow.md" in text
    assert "docs/project_packet_contract.md" in text
    assert "docs/projects/trader.md" in text
    assert "examples/generic_python_powershell_patch.json" in text
    assert "examples/trader_first_verify_patch.json" in text

def test_f8_docs_name_the_final_bundle_explicitly() -> None:
    project_status = (PROJECT_ROOT / "docs/project_status.md").read_text(encoding="utf-8").lower()
    llm_usage = (PROJECT_ROOT / "docs/llm_usage.md").read_text(encoding="utf-8").lower()
    handoff_surface = (PROJECT_ROOT / "docs/handoff_surface.md").read_text(encoding="utf-8").lower()
    finalization = (PROJECT_ROOT / "docs/finalization_master_plan.md").read_text(encoding="utf-8").lower()
    patch_ledger = (PROJECT_ROOT / "docs/patch_ledger.md").read_text(encoding="utf-8").lower()

    assert "handoff/final_future_llm_source_bundle.txt" in project_status
    assert "handoff/final_future_llm_source_bundle.txt" in llm_usage
    assert "handoff/final_future_llm_source_bundle.txt" in handoff_surface
    assert "handoff/final_future_llm_source_bundle.txt" in finalization
    assert "## patch 132" in patch_ledger
    assert "freeze-export patch" in patch_ledger
""").strip() + "\n"

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python_powershell",
    "target_project_root": str(wrapper_root).replace("\\", "/"),
    "backup_files": [
        "docs/project_status.md",
        "docs/patch_ledger.md",
        "docs/llm_usage.md",
        "docs/handoff_surface.md",
        "docs/finalization_master_plan.md",
        "handoff/final_future_llm_source_bundle.txt",
        "tests/test_final_source_bundle_freeze_export.py",
    ],
    "files_to_write": [
        {
            "path": "docs/project_status.md",
            "content": updated_docs["docs/project_status.md"],
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/patch_ledger.md",
            "content": updated_docs["docs/patch_ledger.md"],
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/llm_usage.md",
            "content": updated_docs["docs/llm_usage.md"],
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/handoff_surface.md",
            "content": updated_docs["docs/handoff_surface.md"],
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "docs/finalization_master_plan.md",
            "content": updated_docs["docs/finalization_master_plan.md"],
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "handoff/final_future_llm_source_bundle.txt",
            "content": bundle_text,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_final_source_bundle_freeze_export.py",
            "content": test_text,
            "content_path": None,
            "encoding": "utf-8",
        },
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
        "f8",
        "freeze_export",
        "source_bundle",
        "self_hosted",
    ],
    "notes": "F8 final source bundle freeze-export patch for PatchOps self-hosted finalization.",
}

manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(str(manifest_path))