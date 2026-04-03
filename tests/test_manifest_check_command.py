import json
from pathlib import Path

from patchops.cli import main
from patchops.manifest_templates import build_manifest_template


def test_check_command_accepts_real_example_manifest(capsys):
    exit_code = main(["check", "examples/generic_backup_patch.json"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["issue_count"] == 0
    assert payload["active_profile"] == "generic_python"


def test_check_command_flags_placeholder_template(capsys, tmp_path):
    output_path = tmp_path / "generated" / "generic_verify_template.json"
    template = build_manifest_template(
        profile_name="generic_python",
        mode="verify",
        patch_name="generic_verify_template",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    exit_code = main(["check", str(output_path)])
    assert exit_code == 1

    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert payload["issue_count"] >= 3
    assert any("target_project_root" in issue for issue in payload["issues"])
    assert any("relative/path/to/file.ext" in issue for issue in payload["issues"])
    assert any("placeholder" in issue.lower() for issue in payload["issues"])


def test_check_command_help_mentions_starter_placeholders(capsys):
    try:
        main(["check", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    help_text = capsys.readouterr().out
    assert "starter placeholders" in help_text