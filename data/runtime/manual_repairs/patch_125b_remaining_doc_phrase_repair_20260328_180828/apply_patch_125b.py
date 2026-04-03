from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(r"C:\dev\patchops")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def ensure_line_after_anchor(text: str, anchor: str, line: str) -> str:
    if line in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + line + "\n", 1)
    return text.rstrip() + "\n" + line + "\n"


def ensure_block_after_anchor(text: str, anchor: str, block: str) -> str:
    if block.strip() in text:
        return text
    if anchor in text:
        return text.replace(anchor, anchor + block, 1)
    return text.rstrip() + "\n\n" + block


def patch_llm_usage() -> str:
    path = PROJECT_ROOT / "docs" / "llm_usage.md"
    text = read_text(path)

    exact_phrase = "- prefer narrow repair over broad rewrite"
    if exact_phrase not in text:
        if "## Boundary reminder" in text:
            text = text.replace("## Boundary reminder\n\n", "## Boundary reminder\n\n" + exact_phrase + "\n", 1)
        elif "do not move target-repo business logic into PatchOps" in text:
            text = text.replace(
                "do not move target-repo business logic into PatchOps",
                "do not move target-repo business logic into PatchOps\n- prefer narrow repair over broad rewrite",
                1,
            )
        else:
            text = text.rstrip() + "\n\n## Boundary reminder\n\n- do not move target-repo business logic into PatchOps\n- prefer narrow repair over broad rewrite\n"

    write_text(path, text)
    return "docs/llm_usage.md"


def patch_readme() -> str:
    path = PROJECT_ROOT / "README.md"
    text = read_text(path)

    block = """See also:

- `docs/project_status.md`
- `docs/patch_ledger.md`

"""
    if "`docs/patch_ledger.md`" not in text:
        if "## Consolidation status\n\n" in text:
            text = text.replace("## Consolidation status\n\n", "## Consolidation status\n\n" + block, 1)
        elif "Consolidation status" in text:
            text = ensure_block_after_anchor(text, "Consolidation status\n", "\n" + block)
        else:
            text = text.rstrip() + "\n\n## Consolidation status\n\n" + block

    write_text(path, text)
    return "README.md"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    if not path.exists():
        return "docs/patch_ledger.md (missing)"

    text = read_text(path)
    marker = "<!-- PATCHOPS_PATCH125B_LEDGER:START -->"
    if marker not in text:
        entry = """
<!-- PATCHOPS_PATCH125B_LEDGER:START -->
## Patch 125B

Patch 125B completes the remaining truth-reset wording repair.

It restores:
- the exact `prefer narrow repair over broad rewrite` phrase in `docs/llm_usage.md`,
- the explicit `docs/patch_ledger.md` reference in `README.md`.

This remains a narrow documentation repair patch.
<!-- PATCHOPS_PATCH125B_LEDGER:END -->
"""
        text = text.rstrip() + "\n" + entry.strip() + "\n"
        write_text(path, text)

    return "docs/patch_ledger.md"


def main() -> int:
    changed = [
        patch_llm_usage(),
        patch_readme(),
        patch_ledger(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
