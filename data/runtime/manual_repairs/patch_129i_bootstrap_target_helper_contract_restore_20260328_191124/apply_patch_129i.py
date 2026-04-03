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


def replace_bootstrap_target_branch(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None

    for idx, line in enumerate(lines):
        if line.startswith('    if args.command == "bootstrap-target":'):
            start = idx
            break

    if start is None:
        raise RuntimeError('Could not find bootstrap-target branch in patchops/cli.py.')

    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if line.startswith('    if args.command == "') and idx > start:
            end = idx
            break
        if line.startswith('if __name__ == "__main__":'):
            end = idx
            break

    if end is None:
        end = len(lines)

    branch = textwrap.dedent(
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
                wrapper_project_root=bootstrap_args.wrapper_root,
                runtime_path=bootstrap_args.runtime_override,
                initial_goals=list(bootstrap_args.initial_goal or []),
                current_stage="Initial onboarding",
            )
            print(json.dumps(payload, indent=2))
            return 0
        '''
    ).strip('\n').splitlines()

    indented_branch = [('    ' + line) if line else '' for line in branch]
    new_lines = lines[:start] + indented_branch + lines[end:]
    return '\n'.join(new_lines) + '\n'


def patch_cli() -> str:
    path = PROJECT_ROOT / "patchops" / "cli.py"
    text = read_text(path)

    if "import sys" not in text:
        if "import json\n" in text:
            text = text.replace("import json\n", "import json\nimport sys\n", 1)
        else:
            text = "import sys\n" + text

    text = replace_bootstrap_target_branch(text)
    write_text(path, text)
    return "patchops/cli.py"


def patch_bootstrap_target_cli_test() -> str:
    path = PROJECT_ROOT / "tests" / "test_bootstrap_target_cli_current.py"
    text = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        import subprocess
        import sys
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]


        def test_bootstrap_target_cli_current_module_invocation(tmp_path: Path) -> None:
            target_root = tmp_path / "demo_target"
            target_root.mkdir(parents=True, exist_ok=True)

            wrapper_root = tmp_path / "wrapper_root"
            wrapper_root.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable,
                "-m",
                "patchops.cli",
                "bootstrap-target",
                "--project-name",
                "Demo Bootstrap CLI",
                "--target-root",
                str(target_root),
                "--profile",
                "generic_python",
                "--wrapper-root",
                str(wrapper_root),
                "--initial-goal",
                "Create the first packet",
                "--initial-goal",
                "Generate the safest starter manifest",
            ]

            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, result.stderr

            onboarding_root = wrapper_root / "onboarding"
            bootstrap_md = onboarding_root / "current_target_bootstrap.md"
            bootstrap_json = onboarding_root / "current_target_bootstrap.json"
            next_prompt = onboarding_root / "next_prompt.txt"
            starter_manifest = onboarding_root / "starter_manifest.json"

            assert bootstrap_md.exists()
            assert bootstrap_json.exists()
            assert next_prompt.exists()
            assert starter_manifest.exists()

            payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
            assert payload["project_name"] == "Demo Bootstrap CLI"
            assert payload["profile_name"] == "generic_python"
            assert payload["current_stage"] == "Initial onboarding"
            assert Path(payload["project_packet_path"]).name == "demo_bootstrap_cli.md"
            assert payload["recommended_commands"] == ["check", "inspect", "plan", "apply_or_verify_only"]
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_bootstrap_target_cli_current.py"


def patch_new_target_onboarding_test() -> str:
    path = PROJECT_ROOT / "tests" / "test_new_target_onboarding_current.py"
    text = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        PACKET_PATH = PROJECT_ROOT / "docs" / "projects" / "demo_roundtrip_current.md"
        BOOTSTRAP_ROOT = PROJECT_ROOT / "onboarding"


        def test_current_demo_project_packet_exists_and_is_target_facing() -> None:
            assert PACKET_PATH.exists(), f"Missing demo packet: {PACKET_PATH}"

            text = PACKET_PATH.read_text(encoding="utf-8")
            lowered = text.lower()

            assert "project packet" in lowered
            assert "demo roundtrip current" in lowered
            assert "selected patchops profile" in lowered
            assert "what must remain outside patchops" in lowered
            assert "current development state" in lowered or "current state" in lowered


        def test_current_onboarding_bootstrap_artifacts_exist() -> None:
            required = [
                BOOTSTRAP_ROOT / "current_target_bootstrap.md",
                BOOTSTRAP_ROOT / "current_target_bootstrap.json",
                BOOTSTRAP_ROOT / "next_prompt.txt",
                BOOTSTRAP_ROOT / "starter_manifest.json",
            ]
            for path in required:
                assert path.exists(), f"Missing onboarding artifact: {path}"


        def test_current_onboarding_bootstrap_payload_matches_demo_target() -> None:
            payload = json.loads((BOOTSTRAP_ROOT / "current_target_bootstrap.json").read_text(encoding="utf-8"))
            starter_manifest = json.loads((BOOTSTRAP_ROOT / "starter_manifest.json").read_text(encoding="utf-8"))
            bootstrap_md = (BOOTSTRAP_ROOT / "current_target_bootstrap.md").read_text(encoding="utf-8")
            next_prompt = (BOOTSTRAP_ROOT / "next_prompt.txt").read_text(encoding="utf-8")

            assert payload["project_name"] == "Demo Roundtrip Current"
            assert payload["profile_name"] == "generic_python"
            assert payload["current_stage"] == "Initial onboarding"
            assert Path(payload["project_packet_path"]) == PACKET_PATH.resolve()
            assert payload["recommended_commands"] == ["check", "inspect", "plan", "apply_or_verify_only"]

            assert Path(payload["bootstrap_markdown_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.md").resolve()
            assert Path(payload["bootstrap_json_path"]) == (BOOTSTRAP_ROOT / "current_target_bootstrap.json").resolve()
            assert Path(payload["next_prompt_path"]) == (BOOTSTRAP_ROOT / "next_prompt.txt").resolve()
            assert Path(payload["starter_manifest_path"]) == (BOOTSTRAP_ROOT / "starter_manifest.json").resolve()

            assert starter_manifest["active_profile"] == "generic_python"
            assert starter_manifest["patch_name"] == "bootstrap_verify_only"
            assert starter_manifest["target_project_root"]

            assert "# Onboarding bootstrap - Demo Roundtrip Current" in bootstrap_md
            assert "## 2. Suggested reading order" in bootstrap_md
            assert "docs/project_packet_contract.md" in bootstrap_md
            assert "docs/project_packet_workflow.md" in bootstrap_md
            assert "## 4. Recommended command order" in bootstrap_md

            assert "You are onboarding the target project 'Demo Roundtrip Current' into PatchOps." in next_prompt
            assert "Read the generic PatchOps packet first, then use the project packet." in next_prompt
            assert "Selected profile: generic_python" in next_prompt
            assert "Then run check, inspect, and plan before any apply or verify-only execution." in next_prompt


        def test_status_and_finalization_docs_track_patch_129_onboarding_proof() -> None:
            project_status = (PROJECT_ROOT / "docs" / "project_status.md").read_text(encoding="utf-8")
            finalization_master = (PROJECT_ROOT / "docs" / "finalization_master_plan.md").read_text(encoding="utf-8")

            assert "## Patch 129 - new-target onboarding flow proof" in project_status
            assert "latest confirmed green head: Patch 129" in project_status
            assert "remaining finalization sequence is F6 through F8, not a redesign wave" in project_status

            assert "## Patch 129 - prove new-target onboarding flow" in finalization_master
            assert "- **Latest confirmed green head:** Patch 129" in finalization_master
            assert "- **F6 — final release / maintenance gate**" in finalization_master
        """
    ).strip() + "\n"
    write_text(path, text)
    return "tests/test_new_target_onboarding_current.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129I

        Patch 129I restores the intended helper-backed onboarding bootstrap contract for the `bootstrap-target` command.

        It replaces the current branch with a direct `build_onboarding_bootstrap(...)` call and restores the F5 proof tests to the intended contract:
        - `profile_name`
        - `project_packet_path`
        - `current_stage`
        - `recommended_commands`
        - starter manifest `patch_name = bootstrap_verify_only`
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129I_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129I_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129I - bootstrap-target helper contract restore

        Patch 129I restores the intended helper-backed onboarding bootstrap contract for the `bootstrap-target` CLI branch.

        This is still a narrow onboarding-proof repair patch.
        It does not redesign onboarding; it makes the CLI branch honor the maintained helper contract already documented in the repo.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129I_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129I_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def main() -> int:
    changed = [
        patch_cli(),
        patch_bootstrap_target_cli_test(),
        patch_new_target_onboarding_test(),
        patch_ledger(),
        patch_status(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
