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

    required_import = "from patchops.project_packets import build_onboarding_bootstrap"
    if required_import not in text:
        raise RuntimeError("Expected build_onboarding_bootstrap import is missing; narrow patch cannot continue safely.")

    patterns = [
        (r'"selected_profile"\s*:\s*profile_name,?', '"profile_name": profile_name,'),
        (r'"packet_path"\s*:\s*str\([^)]*\),?', '"project_packet_path": str(resolved_packet_path),'),
        (r'"wrapper_root"\s*:\s*str\([^)]*\),?', '"wrapper_project_root": str(wrapper_root),'),
        (r'"runtime_override"\s*:\s*runtime_override,?', '"runtime_path": runtime_override,'),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)

    # Ensure current_stage is present in the emitted payload block.
    if '"current_stage": current_stage,' not in text:
        text = text.replace(
            '"project_packet_path": str(resolved_packet_path),',
            '"project_packet_path": str(resolved_packet_path),\n        "current_stage": current_stage,',
            1,
        )

    # Ensure recommended_commands is present.
    if '"recommended_commands": ["check", "inspect", "plan", "apply_or_verify_only"],' not in text:
        text = text.replace(
            '"initial_goals": list(initial_goals),',
            '"initial_goals": list(initial_goals),\n        "recommended_commands": ["check", "inspect", "plan", "apply_or_verify_only"],',
            1,
        )

    # Ensure next_prompt_path stays aligned with the helper contract.
    if '"next_prompt_path": str((onboarding_root / "next_prompt.txt").resolve()),' not in text:
        text = text.replace(
            '"starter_manifest_path": str((onboarding_root / "starter_manifest.json").resolve()),',
            '"starter_manifest_path": str((onboarding_root / "starter_manifest.json").resolve()),\n        "next_prompt_path": str((onboarding_root / "next_prompt.txt").resolve()),',
            1,
        )

    write_text(path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129D

        Patch 129D repairs the final payload-shape mismatch in the `bootstrap-target` onboarding proof path.

        The maintained onboarding bootstrap contract expects fields such as:
        - `profile_name`
        - `project_packet_path`
        - `current_stage`
        - `recommended_commands`

        Patch 129D aligns the `bootstrap-target` CLI output with that existing helper contract and then reruns the onboarding proof.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129D_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129D_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129D - bootstrap-target payload contract repair

        Patch 129D is a narrow payload-contract repair for the onboarding proof path.

        It keeps the CLI flow and onboarding artifacts intact and only aligns the emitted bootstrap JSON with the maintained helper contract already expected by the repo tests.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129D_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129D_STATUS:END -->",
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
