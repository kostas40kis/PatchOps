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
        ## Patch 129A

        Patch 129A repairs the narrow bootstrap-artifact failure left by Patch 129.

        The onboarding proof itself was already mostly successful:
        - `recommend-profile` passed,
        - `init-project-doc` passed,
        - `starter` passed.

        The only broken step was the ad hoc helper used to call bootstrap generation.
        Patch 129A replaces that ad hoc proof step with the built-in `bootstrap-target` CLI surface and leaves the broader onboarding design unchanged.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129A_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129A_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129A - onboarding bootstrap CLI repair

        Patch 129A is a narrow repair patch for the onboarding proof wave.

        It does not redesign onboarding.
        It only replaces the failed ad hoc bootstrap helper with the maintained `bootstrap-target` command surface so the expected onboarding artifacts are generated under `onboarding/`.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129A_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129A_STATUS:END -->",
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
