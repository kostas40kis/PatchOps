from pathlib import Path

from patchops.models import Manifest
from patchops.profiles.trader import build_profile


def test_trader_profile_has_expected_defaults():
    profile = build_profile(Manifest(manifest_version="1", patch_name="x", active_profile="trader"), Path("."))
    assert profile.name == "trader"
    assert "trader" in str(profile.default_target_root)
    normalized = str(profile.runtime_path).replace('\\', '/').replace('\\', '/')
    assert normalized.endswith('.venv/Scripts/python.exe')
