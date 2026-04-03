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

    if "import sys" not in text:
        if "import json\n" in text:
            text = text.replace("import json\n", "import json\nimport sys\n", 1)
        else:
            text = "import sys\n" + text

    old_line = "bootstrap_args = bootstrap_parser.parse_args(argv[1:])"
    new_block = (
        "bootstrap_argv = sys.argv[1:] if argv is None else argv[1:]\n"
        "        bootstrap_args = bootstrap_parser.parse_args(bootstrap_argv)"
    )

    if old_line in text:
        text = text.replace(old_line, new_block, 1)
    elif "bootstrap_parser.parse_args(bootstrap_argv)" not in text:
        pattern = re.compile(r"(?m)^(\s*)bootstrap_args = bootstrap_parser\.parse_args\(argv\[1:\]\)\s*$")
        text, count = pattern.subn(r"\1bootstrap_argv = sys.argv[1:] if argv is None else argv[1:]\n\1bootstrap_args = bootstrap_parser.parse_args(bootstrap_argv)", text, count=1)
        if count == 0:
            raise RuntimeError("Could not find bootstrap-target parse_args line to patch.")

    write_text(path, text)
    return "patchops/cli.py"


def patch_ledger() -> str:
    path = PROJECT_ROOT / "docs" / "patch_ledger.md"
    block = textwrap.dedent(
        """
        ## Patch 129B

        Patch 129B repairs the narrow `bootstrap-target` CLI branch bug revealed by the onboarding proof wave.

        The failure was not in onboarding design or bootstrap generation.
        The failure was that the `bootstrap-target` branch tried to parse `argv[1:]` even when `main()` had been entered with `argv=None`.

        Patch 129B changes that branch to use `sys.argv[1:]` in the `argv is None` case and then reruns the current onboarding proof.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129B_LEDGER:START -->",
        "<!-- PATCHOPS_PATCH129B_LEDGER:END -->",
        block,
    )
    return "docs/patch_ledger.md"


def patch_status() -> str:
    path = PROJECT_ROOT / "docs" / "project_status.md"
    block = textwrap.dedent(
        """
        ## Patch 129B - bootstrap-target argv repair

        Patch 129B is a narrow CLI repair for the onboarding proof path.

        It does not redesign onboarding.
        It only fixes the `bootstrap-target` module-entry branch so the current onboarding artifacts can be generated through the maintained CLI surface.
        """
    ).strip()

    upsert_marked_block(
        path,
        "<!-- PATCHOPS_PATCH129B_STATUS:START -->",
        "<!-- PATCHOPS_PATCH129B_STATUS:END -->",
        block,
    )
    return "docs/project_status.md"


def write_cli_test() -> str:
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
        """
    ).strip() + "\n"

    write_text(path, text)
    return "tests/test_bootstrap_target_cli_current.py"


def main() -> int:
    changed = [
        patch_cli(),
        patch_ledger(),
        patch_status(),
        write_cli_test(),
    ]
    for item in changed:
        print(f"WROTE : {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
