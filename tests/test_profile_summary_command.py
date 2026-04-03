import json

from patchops.cli import main


def test_profiles_command_prints_all_profiles(capsys):
    exit_code = main(["profiles"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    names = {item["name"] for item in payload}

    assert "trader" in names
    assert "generic_python" in names
    assert "generic_python_powershell" in names


def test_profiles_command_prints_single_profile(capsys):
    exit_code = main(["profiles", "--name", "trader"])
    assert exit_code == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["name"] == "trader"
    assert payload["report_prefix"] == "trader_patch"
    assert payload["strict_one_report"] is True