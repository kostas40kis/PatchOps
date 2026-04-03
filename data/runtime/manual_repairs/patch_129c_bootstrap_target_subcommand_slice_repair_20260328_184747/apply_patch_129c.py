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


def patch_cli() -> str:
    path = PROJECT_ROOT / "patchops" / "cli.py"
    text = read_text(path)

    old = "bootstrap_argv = sys.argv[1:] if argv is None else argv[1:]"
    new = "bootstrap_argv = sys.argv[2:] if argv is None else argv[1:]"

    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("Expected bootstrap_argv line was not found for narrow repair.")

    write_text(path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        '''
        ## Patch 129C

        Patch 129C completes the narrow `bootstrap-target` CLI repair.

        Patch 129B fixed the `argv is None` crash.
        Patch 129C fixes the remaining subcommand-token issue by ensuring the bootstrap-target branch uses `sys.argv[2:]` for module-entry invocation while preserving `argv[1:]` for direct `main([...])` calls.

        This patch still does not redesign onboarding.
        It only repairs the CLI argument slicing so the current onboarding artifacts can be generated through the maintained command surface.
        '''
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129C_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129C_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        '''
        ## Patch 129C - bootstrap-target subcommand slice repair

        Patch 129C is the second narrow CLI repair for the onboarding proof path.

        It preserves the Patch 129 / 129A / 129B onboarding design and only fixes the final argument-slicing detail needed for successful `python -m patchops.cli bootstrap-target ...` execution.
        '''
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129C_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129C_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        patch_cli(),
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
