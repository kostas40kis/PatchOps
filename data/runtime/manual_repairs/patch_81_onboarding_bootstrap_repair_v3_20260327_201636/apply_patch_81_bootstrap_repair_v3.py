from __future__ import annotations

import json
import re
from pathlib import Path


TEST_FILE = """from __future__ import annotations

import json
from pathlib import Path

from patchops.project_packets import bootstrap_target


def test_bootstrap_target_writes_expected_artifacts(tmp_path) -> None:
    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(
        json.dumps(
            {
                "next_action": "Build the first packet.",
                "latest_passed_patch": "patch_80",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = bootstrap_target(
        project_name="Demo Target",
        target_root=r"C:\\dev\\demo",
        wrapper_project_root=tmp_path,
        profile_name="generic_python",
        starter_intent="documentation_patch",
        runtime_path="py",
        handoff_json_path=handoff_path,
    )

    onboarding_dir = tmp_path / "onboarding"
    assert payload["project_name"] == "Demo Target"
    assert payload["onboarding_dir"] == str(onboarding_dir.resolve())
    assert (onboarding_dir / "current_target_bootstrap.md").exists()
    assert (onboarding_dir / "current_target_bootstrap.json").exists()
    assert (onboarding_dir / "next_prompt.txt").exists()
    assert (onboarding_dir / "starter_manifest.json").exists()

    prompt_text = (onboarding_dir / "next_prompt.txt").read_text(encoding="utf-8")
    assert "Demo Target" in prompt_text
    assert "documentation_patch" in prompt_text


def test_bootstrap_target_cli_accepts_starter_intent(tmp_path, monkeypatch, capsys) -> None:
    from patchops import cli

    monkeypatch.chdir(tmp_path)

    argv = [
        "patchops",
        "bootstrap-target",
        "--name",
        "Demo Target",
        "--target-root",
        r"C:\\dev\\demo",
        "--profile",
        "generic_python",
        "--starter-intent",
        "documentation_patch",
    ]

    monkeypatch.setattr("sys.argv", argv)
    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["project_name"] == "Demo Target"
"""

def replace_or_append_block(text: str, start_marker: str, end_marker: str, block: str) -> str:
    if start_marker in text and end_marker in text:
        prefix = text.split(start_marker, 1)[0]
        suffix = text.split(end_marker, 1)[1]
        if prefix and not prefix.endswith("\\n"):
            prefix += "\\n"
        if suffix and not suffix.startswith("\\n"):
            suffix = "\\n" + suffix
        return prefix + block + suffix
    return text.rstrip() + "\\n\\n" + block + "\\n"

def find_matching_paren(text: str, open_paren_index: int) -> int:
    depth = 0
    for index in range(open_paren_index, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError("Could not find matching parenthesis.")

def get_function_signature_params(text: str, func_name: str) -> list[str]:
    match = re.search(rf"def\\s+{re.escape(func_name)}\\s*\\(", text)
    if not match:
        return []
    open_paren_index = match.end() - 1
    close_paren_index = find_matching_paren(text, open_paren_index)
    signature = text[open_paren_index + 1:close_paren_index]
    params: list[str] = []
    for raw_part in signature.split(","):
        piece = raw_part.strip()
        if not piece:
            continue
        if piece.startswith("*"):
            piece = piece.lstrip("*").strip()
        if not piece:
            continue
        name = piece.split(":", 1)[0].split("=", 1)[0].strip()
        if name:
            params.append(name)
    return params

def replace_kwarg_in_builder_call(text: str) -> str:
    builder_names = re.findall(r"def\\s+(\\w*bootstrap\\w*markdown\\w*)\\s*\\(", text)
    for builder_name in builder_names:
        params = get_function_signature_params(text, builder_name)
        search_start = 0
        while True:
            call_index = text.find(builder_name + "(", search_start)
            if call_index == -1:
                break
            open_paren_index = text.find("(", call_index)
            close_paren_index = find_matching_paren(text, open_paren_index)
            call_block = text[call_index:close_paren_index + 1]
            if "runtime_path=" in call_block and "runtime_path" not in params and "runtime_override" in params:
                updated_call_block = call_block.replace("runtime_path=", "runtime_override=")
                return text[:call_index] + updated_call_block + text[close_paren_index + 1:]
            if "runtime_override=" in call_block and "runtime_override" not in params and "runtime_path" in params:
                updated_call_block = call_block.replace("runtime_override=", "runtime_path=")
                return text[:call_index] + updated_call_block + text[close_paren_index + 1:]
            search_start = close_paren_index + 1
    return text

def ensure_bootstrap_parser_argument(cli_text: str) -> str:
    if "--starter-intent" in cli_text:
        return cli_text

    parser_match = re.search(
        r"^(?P<indent>\\s*)(?P<var>\\w+)\\s*=\\s*subparsers\\.add_parser\\((?P<body>.*?)\\)\\s*$",
        cli_text,
        re.MULTILINE | re.DOTALL,
    )
    bootstrap_var = None
    for match in re.finditer(
        r"^(?P<indent>\\s*)(?P<var>\\w+)\\s*=\\s*subparsers\\.add_parser\\((?P<body>.*?)\\)\\s*$",
        cli_text,
        re.MULTILINE,
    ):
        body = match.group("body")
        if "bootstrap-target" in body:
            bootstrap_var = match.group("var")
            line_end = cli_text.find("\\n", match.end())
            if line_end == -1:
                line_end = len(cli_text)
            insertion = f"\\n{match.group('indent')}{bootstrap_var}.add_argument('--starter-intent', default='documentation_patch')"
            return cli_text[:line_end] + insertion + cli_text[line_end:]
    raise RuntimeError("Could not find bootstrap-target parser declaration.")

def ensure_bootstrap_branch_uses_args_command(cli_text: str) -> str:
    cli_text = re.sub(
        r"if\\s+command\\s*==\\s*['\\\"]bootstrap-target['\\\"]\\s*:",
        'if args.command == "bootstrap-target":',
        cli_text,
    )
    return cli_text

def ensure_bootstrap_call_has_starter_intent(cli_text: str) -> str:
    call_index = cli_text.find("bootstrap_target(")
    if call_index == -1:
        raise RuntimeError("Could not find bootstrap_target call in cli.py.")
    open_paren_index = cli_text.find("(", call_index)
    close_paren_index = find_matching_paren(cli_text, open_paren_index)
    call_block = cli_text[call_index:close_paren_index + 1]
    if "starter_intent=" in call_block:
        return cli_text
    lines = call_block.splitlines()
    if len(lines) == 1:
        updated_call_block = call_block[:-1] + ", starter_intent=args.starter_intent)"
    else:
        indent = " " * 12
        updated_lines = lines[:-1] + [f"{indent}starter_intent=args.starter_intent,", lines[-1]]
        updated_call_block = "\\n".join(updated_lines)
    return cli_text[:call_index] + updated_call_block + cli_text[close_paren_index + 1:]

def ensure_cli_json_not_shadowed(cli_text: str) -> str:
    cli_text = re.sub(r"^\\s*import\\s+json\\s*$", "", cli_text, flags=re.MULTILINE)
    if "import json" not in cli_text.splitlines()[:20]:
        cli_text = "import json\\n" + cli_text.lstrip()
    return cli_text

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"
    test_path = root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    cli_text = cli_path.read_text(encoding="utf-8")
    packets_text = packets_path.read_text(encoding="utf-8")

    packets_text = replace_kwarg_in_builder_call(packets_text)
    cli_text = ensure_cli_json_not_shadowed(cli_text)
    cli_text = ensure_bootstrap_branch_uses_args_command(cli_text)
    cli_text = ensure_bootstrap_parser_argument(cli_text)
    cli_text = ensure_bootstrap_call_has_starter_intent(cli_text)

    cli_path.write_text(cli_text, encoding="utf-8")
    packets_path.write_text(packets_text, encoding="utf-8")
    test_path.write_text(TEST_FILE, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [
                    str(cli_path),
                    str(packets_path),
                    str(test_path),
                ]
            },
            indent=2,
        )
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())