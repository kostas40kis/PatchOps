from __future__ import annotations

import json
import re
from pathlib import Path


def ensure_bootstrap_parser_arg(cli_text: str) -> str:
    if "--starter-intent" in cli_text:
        return cli_text
    pattern = re.compile(
        r'(?P<var>\w+)\s*=\s*subparsers\.add_parser\(\s*"bootstrap-target"[\s\S]*?\)\n',
        re.MULTILINE,
    )
    match = pattern.search(cli_text)
    if not match:
        raise SystemExit("Could not locate bootstrap-target parser definition in cli.py")
    var_name = match.group("var")
    insert = f'{var_name}.add_argument("--starter-intent", default="documentation_patch")\n'
    return cli_text[: match.end()] + insert + cli_text[match.end() :]


def ensure_bootstrap_call_kwarg(cli_text: str) -> str:
    pattern = re.compile(
        r'payload\s*=\s*bootstrap_target_onboarding\(\n(?P<body>(?:[ \t]+.*\n)+?)[ \t]*\)',
        re.MULTILINE,
    )
    match = pattern.search(cli_text)
    if not match:
        raise SystemExit("Could not locate bootstrap_target_onboarding(...) call in cli.py")
    body = match.group("body")
    if "starter_intent=" in body:
        return cli_text
    if "initial_goals=args.initial_goal,\n" in body:
        body = body.replace(
            "initial_goals=args.initial_goal,\n",
            'initial_goals=args.initial_goal,\n        starter_intent=args.starter_intent,\n',
        )
    else:
        body = body + '        starter_intent=args.starter_intent,\n'
    new_block = 'payload = bootstrap_target_onboarding(\n' + body + '    )'
    return cli_text[: match.start()] + new_block + cli_text[match.end() :]


def remove_local_json_import(cli_text: str) -> str:
    return cli_text.replace("\n        import json\n", "\n")


def remove_bad_builder_kwarg(packets_text: str) -> str:
    pattern = re.compile(
        r'md_text\s*=\s*_build_current_target_bootstrap_markdown\(\n(?P<body>(?:[ \t]+.*\n)+?)[ \t]*\)',
        re.MULTILINE,
    )
    match = pattern.search(packets_text)
    if not match:
        raise SystemExit("Could not locate _build_current_target_bootstrap_markdown(...) call in project_packets.py")
    body = match.group("body")
    new_body = re.sub(
        r'[ \t]*runtime_(?:path|override)\s*=\s*runtime_override,\n',
        "",
        body,
    )
    new_block = 'md_text = _build_current_target_bootstrap_markdown(\n' + new_body + '    )'
    return packets_text[: match.start()] + new_block + packets_text[match.end() :]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"

    cli_text = cli_path.read_text(encoding="utf-8")
    packets_text = packets_path.read_text(encoding="utf-8")

    cli_text = remove_local_json_import(cli_text)
    cli_text = ensure_bootstrap_parser_arg(cli_text)
    cli_text = ensure_bootstrap_call_kwarg(cli_text)
    packets_text = remove_bad_builder_kwarg(packets_text)

    cli_path.write_text(cli_text, encoding="utf-8")
    packets_path.write_text(packets_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [
                    str(cli_path),
                    str(packets_path),
                ]
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())