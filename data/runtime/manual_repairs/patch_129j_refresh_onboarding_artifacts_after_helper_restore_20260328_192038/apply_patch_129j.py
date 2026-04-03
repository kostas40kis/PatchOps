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


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129J

        Patch 129J refreshes the generated onboarding artifacts after the helper-contract restore work.

        The remaining failure after Patch 129I was not a code-logic failure.
        It was that `onboarding/current_target_bootstrap.json` and related artifacts had not been regenerated from the current `bootstrap-target` branch.

        Patch 129J reruns the maintained onboarding bootstrap command against the current demo target and validates the refreshed artifacts.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129J_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129J_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129J - onboarding artifact refresh after helper restore

        Patch 129J is a narrow refresh patch for the F5 onboarding proof stream.

        It does not change the bootstrap contract.
        It regenerates the onboarding artifacts from the current `bootstrap-target` implementation so the repo state matches the now-maintained onboarding proof expectations.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129J_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129J_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
