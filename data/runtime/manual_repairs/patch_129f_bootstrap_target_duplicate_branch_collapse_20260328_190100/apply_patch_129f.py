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

    canonical_block = textwrap.dedent(
        """
        if args.command == "bootstrap-target":
            import argparse

            from patchops.project_packets import build_onboarding_bootstrap

            bootstrap_parser = argparse.ArgumentParser(prog="patchops bootstrap-target")
            bootstrap_parser.add_argument("--project-name", required=True)
            bootstrap_parser.add_argument("--target-root", required=True)
            bootstrap_parser.add_argument("--profile", required=True)
            bootstrap_parser.add_argument("--wrapper-root", default=".")
            bootstrap_parser.add_argument("--runtime-override", default=None)
            bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")
            bootstrap_parser.add_argument("--initial-goal", action="append", default=[])

            bootstrap_argv = sys.argv[2:] if argv is None else argv[1:]
            bootstrap_args = bootstrap_parser.parse_args(bootstrap_argv)

            wrapper_root = bootstrap_args.wrapper_root or str(Path.cwd())
            payload = build_onboarding_bootstrap(
                project_name=bootstrap_args.project_name,
                target_root=bootstrap_args.target_root,
                profile_name=bootstrap_args.profile,
                wrapper_project_root=wrapper_root,
                runtime_path=bootstrap_args.runtime_override,
                initial_goals=list(bootstrap_args.initial_goal or []),
                current_stage="Initial onboarding",
                starter_intent=bootstrap_args.starter_intent,
            )
            print(json.dumps(payload, indent=2))
            return 0
        """
    ).strip("\n")

    pattern = re.compile(
        r'^\s*if args\.command == "bootstrap-target":.*?^\s*return 0\s*$'
        r'(?:\n\s*\n\s*if args\.command == "bootstrap-target":.*?^\s*return 0\s*$)?',
        re.DOTALL | re.MULTILINE,
    )

    match = pattern.search(text)
    if not match:
        raise RuntimeError("Could not locate bootstrap-target branch block for collapse repair.")

    text = pattern.sub(canonical_block, text, count=1)
    write_text(path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129F

        Patch 129F collapses the duplicate `bootstrap-target` branches in `patchops/cli.py` into one canonical branch.

        This resolves the real root cause behind the repeated onboarding-proof failures:
        - one older branch still used `bootstrap_target_onboarding(...)`,
        - one later branch imported `build_onboarding_bootstrap(...)`,
        - the duplicated in-function import created a local-name scoping conflict,
        - and the two branches drifted in payload shape.

        Patch 129F keeps only one `bootstrap-target` branch and routes it through `build_onboarding_bootstrap(...)`.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129F_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129F_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129F - bootstrap-target duplicate branch collapse

        Patch 129F is the final narrow onboarding-proof repair attempt.

        It removes the duplicated `bootstrap-target` command branches and leaves one canonical helper-backed path.
        This is still a CLI-surface repair, not an onboarding redesign.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129F_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129F_STATUS:END -->",
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
