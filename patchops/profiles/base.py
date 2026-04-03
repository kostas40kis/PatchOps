from __future__ import annotations

from pathlib import Path

from patchops.exceptions import ProfileResolutionError
from patchops.models import Manifest, ResolvedProfile
from patchops.profiles import generic_python, generic_python_powershell, trader


PROFILE_FACTORIES = {
    "generic_python": generic_python.build_profile,
    "generic_python_powershell": generic_python_powershell.build_profile,
    "trader": trader.build_profile,
}


def resolve_profile(manifest: Manifest, wrapper_project_root: Path) -> ResolvedProfile:
    profile_name = manifest.active_profile
    factory = PROFILE_FACTORIES.get(profile_name)
    if factory is None:
        raise ProfileResolutionError(f"Unknown profile: {profile_name}")
    return factory(manifest=manifest, wrapper_project_root=wrapper_project_root)
