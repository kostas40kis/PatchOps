import json

from patchops.cli import main


def test_template_command_for_trader_apply(capsys):
    exit_code = main(["template", "--profile", "trader", "--mode", "apply", "--patch-name", "trader_template"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["patch_name"] == "trader_template"
    assert payload["active_profile"] == "trader"
    assert payload["target_project_root"] is not None
    assert payload["target_project_root"].lower().endswith("trader")
    assert payload["backup_files"] == ["relative/path/to/file.ext"]
    assert payload["files_to_write"][0]["path"] == "relative/path/to/file.ext"
    assert payload["validation_commands"][0]["use_profile_runtime"] is True


def test_template_command_for_generic_verify(capsys):
    exit_code = main(["template", "--profile", "generic_python", "--mode", "verify"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["active_profile"] == "generic_python"
    assert payload["files_to_write"] == []
    assert payload["backup_files"] == ["relative/path/to/file.ext"]
    assert payload["tags"] == ["template", "generic_python", "verify"]
    assert payload["validation_commands"][0]["name"] == "validation_command"


def test_template_command_respects_target_override(capsys):
    exit_code = main([
        "template",
        "--profile",
        "generic_python",
        "--mode",
        "apply",
        "--target-root",
        r"C:\dev\custom_demo",
    ])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["target_project_root"].lower().endswith("custom_demo")