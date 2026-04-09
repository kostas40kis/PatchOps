from pathlib import Path

from patchops.cli import build_parser


def _parser_choices() -> set[str]:
    parser = build_parser()
    action = next(action for action in parser._actions if getattr(action, "choices", None))
    return set(action.choices.keys())


def test_documented_commands_exist_in_cli_parser() -> None:
    docs_text = "\n".join(
        [
            Path("docs/bundle_contract_packet.md").read_text(encoding="utf-8"),
            Path("docs/maintenance_freeze_packet.md").read_text(encoding="utf-8"),
        ]
    )
    choices = _parser_choices()

    documented_commands = {
        "check",
        "inspect",
        "plan",
        "apply",
        "verify",
        "check-bundle",
        "inspect-bundle",
        "plan-bundle",
        "bundle-doctor",
        "make-bundle",
        "build-bundle",
        "make-proof-bundle",
        "run-package",
        "bundle-entry",
        "maintenance-gate",
        "emit-operator-script",
        "bootstrap-repair",
    }

    for command in documented_commands:
        assert command in docs_text
        assert command in choices


def test_maintenance_closeout_packet_lists_patch_24_expected_proofs() -> None:
    text = Path("docs/maintenance_freeze_packet.md").read_text(encoding="utf-8")
    assert "doc contract tests" in text
    assert "command/doc alignment proof" in text
    assert "maintainer packet completeness check" in text
