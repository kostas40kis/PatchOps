from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(r"C:\dev\patchops")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def ensure_before_heading(text: str, snippet: str, heading: str) -> str:
    if snippet.strip() in text:
        return text
    if heading in text:
        return text.replace(heading, snippet + heading, 1)
    return text.rstrip() + "\n\n" + snippet


def ensure_after_anchor(text: str, anchor: str, snippet: str) -> str:
    if snippet.strip() in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + snippet, 1)
    return text.rstrip() + "\n\n" + snippet


def ensure_append_section(text: str, section: str) -> str:
    if section.strip() in text:
        return text
    return text.rstrip() + "\n\n" + section.rstrip() + "\n"


def ensure_line_present(text: str, line: str, anchor: str | None = None) -> str:
    if line in text:
        return text
    insertion = line + "\n"
    if anchor and anchor in text:
        return text.replace(anchor, anchor + insertion, 1)
    return text.rstrip() + "\n" + insertion


def patch_readme() -> str:
    path = PROJECT_ROOT / "README.md"
    text = read_text(path)

    consolidation_block = """## Consolidation status

PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture.
The initial buildout circle is complete enough that the repo should be treated as a maintained utility rather than an open-ended experiment.

"""
    text = ensure_before_heading(text, consolidation_block, "## Current status")
    text = ensure_line_present(
        text,
        "PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture.",
        anchor="## Consolidation status\n\n",
    )
    write_text(path, text)
    return "README.md"


def patch_llm_usage() -> str:
    path = PROJECT_ROOT / "docs" / "llm_usage.md"
    text = read_text(path)

    rule_line = "- do not move target-repo business logic into PatchOps"
    if rule_line not in text:
        if "- preserve the one-report evidence contract" in text:
            text = text.replace(
                "- preserve the one-report evidence contract",
                "- preserve the one-report evidence contract\n- do not move target-repo business logic into PatchOps",
                1,
            )
        elif "Rules:" in text:
            text = text.replace("Rules:\n", "Rules:\n- do not move target-repo business logic into PatchOps\n", 1)
        else:
            text = text.rstrip() + "\n\n## Boundary reminder\n\n- do not move target-repo business logic into PatchOps\n"

    write_text(path, text)
    return "docs/llm_usage.md"


def patch_project_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    text = read_text(path)

    snapshot_line = "PatchOps is in late Stage 1 / pre-Stage 2 and should be treated as a maintained wrapper utility."
    if snapshot_line not in text:
        if "## Current state snapshot" in text:
            text = text.replace("## Current state snapshot\n\n", "## Current state snapshot\n\n" + snapshot_line + "\n\n", 1)
        else:
            text = text.rstrip() + "\n\n## Current state snapshot\n\n" + snapshot_line + "\n"

    repair_section = """<!-- PATCHOPS_PATCH125A_STATUS:START -->
## Patch 125A - truth-reset doc contract repair

### Current state

- Patch 125A repairs the narrow documentation regressions exposed by the truth-reset audit.
- The maintained status surface is again explicit about the exact thin PowerShell launcher set.
- The maintained status surface again uses the exact-set test for the shipped CLI subcommand surface wording.
- The maintained status surface again keeps explicit that the operator-facing command map is not only partitioned and inventoried, but also bounded.

### Why this matters

- the repo remains in late Stage 1 / pre-Stage 2 maintenance posture,
- the recent maintenance wave continues through maintenance validation rather than redesign,
- future doc drift is more likely to trigger a narrow honest repair.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small exact-set, boundary, inventory, or doc-contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH125A_STATUS:END -->
"""
    text = ensure_append_section(text, repair_section)
    write_text(path, text)
    return "docs/project_status.md"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    if not path.exists():
        return "docs/patch_ledger.md (missing)"

    text = read_text(path)
    entry = """<!-- PATCHOPS_PATCH125A_LEDGER:START -->
## Patch 125A

Patch 125A repairs the narrow documentation regressions exposed by the truth-reset audit.

It restores:
- the `README.md` consolidation-status wording,
- the `docs/project_status.md` late Stage 1 / pre-Stage 2 posture and exact operator-surface phrasing,
- the `docs/llm_usage.md` rule that target-repo business logic must remain outside PatchOps.

This is a narrow maintenance repair patch, not a redesign.
<!-- PATCHOPS_PATCH125A_LEDGER:END -->
"""
    text = ensure_append_section(text, entry)
    write_text(path, text)
    return "docs/patch_ledger.md"


def main() -> int:
    changed = [
        patch_readme(),
        patch_llm_usage(),
        patch_project_status(),
        patch_ledger(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
