from __future__ import annotations

import shutil
import textwrap
from pathlib import Path


PROJECT_ROOT = Path(r"C:\dev\patchops")
RESTORE_CLI_PATH = Path(r"C:\dev\patchops\data\runtime\manual_repairs\patch_129d_bootstrap_target_payload_contract_repair_20260328_185059\backups\patchops\cli.py")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def upsert_marked_block(path: Path, start_marker: str, end_marker: str, body: str) -> None:
    import re

    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}"
    text = read_text(path)
    pattern = re.compile(re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL)

    if pattern.search(text):
        updated = pattern.sub(block, text, count=1)
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"

    write_text(path, updated)


def restore_and_patch_cli() -> str:
    live_path = PROJECT_ROOT / "patchops" / "cli.py"
    shutil.copyfile(RESTORE_CLI_PATH, live_path)

    text = read_text(live_path)

    if "import sys" not in text:
        if "import json\n" in text:
            text = text.replace("import json\n", "import json\nimport sys\n", 1)
        else:
            text = "import sys\n" + text

    old_block = textwrap.dedent(
        '''
        if args.command == "bootstrap-target":
            import argparse

            from patchops.project_packets import bootstrap_target_onboarding

            bootstrap_parser = argparse.ArgumentParser(prog="patchops bootstrap-target")
            bootstrap_parser.add_argument("--project-name", required=True)
            bootstrap_parser.add_argument("--target-root", required=True)
            bootstrap_parser.add_argument("--profile", required=True)
            bootstrap_parser.add_argument("--wrapper-root", default=".")
            bootstrap_parser.add_argument("--runtime-override", default=None)
            bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")
            bootstrap_parser.add_argument("--initial-goal", action="append", default=[])
            bootstrap_args = bootstrap_parser.parse_args(argv[1:])

            payload = bootstrap_target_onboarding(
                project_name=bootstrap_args.project_name,
                target_root=bootstrap_args.target_root,
                profile_name=bootstrap_args.profile,
                wrapper_project_root=bootstrap_args.wrapper_root,
                initial_goals=bootstrap_args.initial_goal,
                runtime_override=bootstrap_args.runtime_override,
                starter_intent=bootstrap_args.starter_intent,
            )
            print(json.dumps(payload, indent=2))
            return 0
        '''
    ).strip("\n")

    new_block = textwrap.dedent(
        '''
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

            payload = build_onboarding_bootstrap(
                project_name=bootstrap_args.project_name,
                target_root=bootstrap_args.target_root,
                profile_name=bootstrap_args.profile,
                runtime_path=bootstrap_args.runtime_override,
                wrapper_project_root=bootstrap_args.wrapper_root,
                initial_goals=list(bootstrap_args.initial_goal or []),
                current_stage="Initial onboarding",
                starter_intent=bootstrap_args.starter_intent,
            )
            print(json.dumps(payload, indent=2))
            return 0
        '''
    ).strip("\n")

    if old_block not in text:
        raise RuntimeError("Expected bootstrap-target baseline block was not found in restored cli.py.")

    text = text.replace(old_block, new_block, 1)
    write_text(live_path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129G

        Patch 129G restores `patchops/cli.py` from the last syntactically valid backup and then applies one narrow bootstrap-target branch repair.

        It does three things only:
        - restores the CLI file after Patch 129F introduced an indentation break,
        - updates the first `bootstrap-target` branch to use `build_onboarding_bootstrap(...)`,
        - keeps the rest of the CLI unchanged.

        This is the smallest safe recovery patch after the structural CLI break.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129G_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129G_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129G - cli restore and bootstrap branch fix

        Patch 129G restores the CLI from the last syntactically valid backup and reapplies the bootstrap-target fix as one narrow branch-level change.

        This is a recovery patch for the onboarding proof stream.
        It is not a redesign of the onboarding system or the broader CLI surface.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129G_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129G_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        restore_and_patch_cli(),
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
