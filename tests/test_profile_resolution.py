from pathlib import Path

from patchops.models import Manifest
from patchops.profiles.base import resolve_profile


def test_profile_resolution_for_generic_python():
    manifest = Manifest(manifest_version="1", patch_name="x", active_profile="generic_python")
    profile = resolve_profile(manifest, Path("."))
    assert profile.name == "generic_python"
