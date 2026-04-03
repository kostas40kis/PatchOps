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

    if "from patchops.project_packets import build_onboarding_bootstrap" not in text:
        if "from pathlib import Path" in text:
            text = text.replace(
                "from pathlib import Path",
                "from pathlib import Path\nfrom patchops.project_packets import build_onboarding_bootstrap",
                1,
            )
        else:
            raise RuntimeError("Could not safely insert build_onboarding_bootstrap import.")

    marker_start = "        # PATCHOPS_PATCH129E_BOOTSTRAP_HELPER_START"
    marker_end = "        # PATCHOPS_PATCH129E_BOOTSTRAP_HELPER_END"

    helper_block = """        # PATCHOPS_PATCH129E_BOOTSTRAP_HELPER_START
        wrapper_root = bootstrap_args.wrapper_root or str(Path.cwd())
        payload = build_onboarding_bootstrap(
            project_name=bootstrap_args.project_name,
            target_root=bootstrap_args.target_root,
            profile_name=bootstrap_args.profile,
            wrapper_project_root=wrapper_root,
            initial_goals=list(bootstrap_args.initial_goal or []),
            current_stage="Initial onboarding",
            runtime_override=bootstrap_args.runtime_override,
            starter_intent=bootstrap_args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0
        # PATCHOPS_PATCH129E_BOOTSTRAP_HELPER_END
"""

    parse_line = "bootstrap_args = bootstrap_parser.parse_args(bootstrap_argv)"
    if marker_start not in text:
        if parse_line not in text:
            raise RuntimeError("Could not find bootstrap-target parse_args line for helper routing repair.")
        text = text.replace(parse_line, parse_line + "\n" + helper_block.rstrip(), 1)
    else:
        pattern = re.compile(
            re.escape(marker_start) + r".*?" + re.escape(marker_end),
            re.DOTALL,
        )
        text = pattern.sub(helper_block.rstrip(), text, count=1)

    write_text(path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129E

        Patch 129E completes the narrow onboarding-proof repair by routing the `bootstrap-target` CLI branch through the maintained `build_onboarding_bootstrap(...)` helper.

        This avoids further payload drift between:
        - the helper contract already proven in onboarding tests,
        - the CLI branch used by `python -m patchops.cli bootstrap-target ...`,
        - and the onboarding artifacts written under `onboarding/`.

        This is still a narrow CLI repair, not an onboarding redesign.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129E_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129E_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129E - bootstrap-target helper routing repair

        Patch 129E routes the `bootstrap-target` CLI branch through the maintained onboarding helper so the emitted payload and generated onboarding artifacts match the already-shipped onboarding bootstrap contract.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129E_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129E_STATUS:END -->",
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
