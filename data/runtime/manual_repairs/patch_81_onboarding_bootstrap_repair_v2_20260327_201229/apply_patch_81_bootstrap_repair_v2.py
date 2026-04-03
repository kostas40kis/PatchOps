from __future__ import annotations

from pathlib import Path


def require_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Could not find expected text for {label}.")
    return text.replace(old, new, 1)


def ensure_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"Expected text missing for {label}.")


def patch_project_packets(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text = require_replace(
        text,
        '        runtime_path=runtime_override,\n',
        '        runtime_override=runtime_override,\n',
        'bootstrap markdown keyword',
    )

    path.write_text(text, encoding="utf-8")


def patch_cli(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    if '--starter-intent' not in text:
        anchor = '    bootstrap_parser.add_argument("--runtime-path", default=None)\n'
        insert = (
            '    bootstrap_parser.add_argument("--runtime-path", default=None)\n'
            '    bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")\n'
        )
        text = require_replace(text, anchor, insert, 'bootstrap parser starter-intent argument')

    old_call = (
        '            initial_goals=args.initial_goals,\n'
        '            runtime_override=args.runtime_path,\n'
        '        )\n'
    )
    if 'starter_intent=args.starter_intent' not in text:
        new_call = (
            '            initial_goals=args.initial_goals,\n'
            '            runtime_override=args.runtime_path,\n'
            '            starter_intent=args.starter_intent,\n'
            '        )\n'
        )
        text = require_replace(text, old_call, new_call, 'bootstrap-target call starter_intent wiring')

    ensure_contains(text, 'elif args.command == "bootstrap-target":', 'bootstrap-target main branch')
    ensure_contains(text, 'starter_intent=args.starter_intent', 'bootstrap-target starter-intent wiring')
    ensure_contains(text, 'bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")', 'bootstrap-target starter-intent parser arg')

    path.write_text(text, encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / 'patchops' / 'cli.py'
    packets_path = root / 'patchops' / 'project_packets.py'

    patch_project_packets(packets_path)
    patch_cli(cli_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())