from __future__ import annotations

from pathlib import Path

import pytest

from patchops import cli


def test_native_zip_transition_doc_exists_and_states_before_after() -> None:
    doc_path = Path("docs/bundle_native_zip_transition.md")
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert "Before this patch series finished:" in text
    assert "After this patch series finished:" in text
    assert "you manually unzipped bundles" in text
    assert "you no longer manually unzip bundles" in text
    assert "PatchOps accepts the `.zip`" in text
    assert "PatchOps extracts it" in text
    assert "PatchOps calls the bundled `.ps1`" in text
    assert "one canonical report" in text


@pytest.mark.parametrize(
    "command_name",
    ["check-bundle", "inspect-bundle", "plan-bundle", "apply-bundle"],
)
def test_native_zip_transition_doc_examples_match_live_cli_help(
    command_name: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([command_name, "--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert f"usage: patchops {command_name}" in text


def test_native_zip_transition_doc_lists_raw_zip_commands() -> None:
    text = Path("docs/bundle_native_zip_transition.md").read_text(encoding="utf-8")
    assert "check-bundle" in text
    assert "inspect-bundle" in text
    assert "plan-bundle" in text
    assert "apply-bundle" in text