from __future__ import annotations

import json
from pathlib import Path

HELPER_BLOCK = r'''
# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_START

def _normalize_target_name(target_root: str) -> str:
    value = str(target_root).replace('\\', '/').rstrip('/')
    if not value:
        return ''
    return value.split('/')[-1].lower()


def recommend_profile_for_target(*, target_root: str, wrapper_project_root=None):
    target_name = _normalize_target_name(target_root)

    if target_name == 'trader':
        recommended_profile = 'trader'
        rationale = (
            'The target root name matches trader, so the dedicated trader profile is the '
            'smallest correct conservative choice.'
        )
        runtime_path = None
        starter_examples = [
            'examples/trader_first_verify_patch.json',
            'examples/trader_first_doc_patch.json',
            'examples/trader_verify_patch.json',
            'examples/trader_doc_patch.json',
        ]
    else:
        recommended_profile = 'generic_python'
        rationale = (
            'No target-specific profile signal was detected, so generic_python is the '
            'smallest conservative default.'
        )
        runtime_path = None
        starter_examples = [
            'examples/generic_python_verify_patch.json',
            'examples/generic_python_doc_patch.json',
        ]

    return {
        'target_root': str(target_root),
        'wrapper_project_root': None if wrapper_project_root is None else str(wrapper_project_root),
        'recommended_profile': recommended_profile,
        'rationale': rationale,
        'expected_runtime_path': runtime_path,
        'starter_examples': starter_examples,
    }

# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_END
'''

TEST_PROFILE = '''from __future__ import annotations

from patchops.project_packets import recommend_profile_for_target


def test_recommend_profile_for_trader_target() -> None:
    payload = recommend_profile_for_target(target_root=r"C:\\dev\\trader")
    assert payload["recommended_profile"] == "trader"
    assert "smallest correct" in payload["rationale"]
    assert "examples/trader_first_verify_patch.json" in payload["starter_examples"]


def test_recommend_profile_for_generic_target() -> None:
    payload = recommend_profile_for_target(target_root=r"C:\\dev\\demo")
    assert payload["recommended_profile"] == "generic_python"
    assert "generic_python" in payload["rationale"]
    assert "examples/generic_python_verify_patch.json" in payload["starter_examples"]
'''

TEST_COMMAND = '''from __future__ import annotations

import json

from patchops.cli import main


def test_recommend_profile_command_prints_json(capsys) -> None:
    exit_code = main([
        "recommend-profile",
        "--target-root",
        r"C:\\dev\\trader",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["recommended_profile"] == "trader"
    assert payload["target_root"] == r"C:\\dev\\trader"
    assert "starter_examples" in payload
'''


def ensure_helper_block(text: str) -> str:
    start = '# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_START'
    end = '# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_END'
    if start in text and end in text:
        prefix = text.split(start, 1)[0]
        suffix = text.split(end, 1)[1]
        return prefix.rstrip() + '\n\n' + HELPER_BLOCK.strip() + '\n' + suffix.lstrip('\n')
    return text.rstrip() + '\n\n' + HELPER_BLOCK.strip() + '\n'


def ensure_cli_parser_block(lines: list[str]) -> list[str]:
    parser_line = '    recommend_profile_parser = subparsers.add_parser("recommend-profile")'
    if any(parser_line in line for line in lines):
        return lines

    anchor = None
    for idx, line in enumerate(lines):
        if 'args = parser.parse_args(argv)' in line:
            anchor = idx
            break
    if anchor is None:
        raise SystemExit('Could not find parser.parse_args(argv) in cli.py.')

    block = [
        '    recommend_profile_parser = subparsers.add_parser("recommend-profile")',
        '    recommend_profile_parser.add_argument("--target-root", required=True)',
        '    recommend_profile_parser.add_argument("--wrapper-root")',
        '',
    ]
    return lines[:anchor] + block + lines[anchor:]


def ensure_cli_main_branch(lines: list[str]) -> list[str]:
    if any('if args.command == "recommend-profile":' in line for line in lines):
        return lines

    anchor = None
    for idx, line in enumerate(lines):
        if 'parser.error("Unknown command")' in line:
            anchor = idx
            break
    if anchor is None:
        raise SystemExit('Could not find parser.error("Unknown command") in cli.py.')

    block = [
        '    if args.command == "recommend-profile":',
        '        payload = recommend_profile_for_target(',
        '            target_root=args.target_root,',
        '            wrapper_project_root=args.wrapper_root,',
        '        )',
        '        print(json.dumps(payload, indent=2))',
        '        return 0',
        '',
    ]
    return lines[:anchor] + block + lines[anchor:]


def ensure_cli_import(lines: list[str]) -> list[str]:
    import_line = '    recommend_profile_for_target,'
    if any(import_line in line for line in lines):
        return lines

    start = None
    end = None
    for idx, line in enumerate(lines):
        if line.startswith('from patchops.project_packets import ('):
            start = idx
            continue
        if start is not None and line.strip() == ')':
            end = idx
            break
    if start is None or end is None:
        raise SystemExit('Could not find project_packets import block in cli.py.')

    insert_at = end
    lines.insert(insert_at, '    recommend_profile_for_target,')
    return lines


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    project_packets = root / 'patchops' / 'project_packets.py'
    cli = root / 'patchops' / 'cli.py'
    test_profile = root / 'tests' / 'test_project_packet_profile_recommendation.py'
    test_command = root / 'tests' / 'test_project_packet_recommend_profile_command.py'

    packets_text = project_packets.read_text(encoding='utf-8')
    packets_text = ensure_helper_block(packets_text)
    project_packets.write_text(packets_text, encoding='utf-8')

    cli_lines = cli.read_text(encoding='utf-8').splitlines()
    cli_lines = ensure_cli_import(cli_lines)
    cli_lines = ensure_cli_parser_block(cli_lines)
    cli_lines = ensure_cli_main_branch(cli_lines)
    cli.write_text('\n'.join(cli_lines) + '\n', encoding='utf-8')

    test_profile.write_text(TEST_PROFILE, encoding='utf-8')
    test_command.write_text(TEST_COMMAND, encoding='utf-8')

    print(
        json.dumps(
            {
                'written_files': [
                    str(project_packets),
                    str(cli),
                    str(test_profile),
                    str(test_command),
                ]
            },
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())