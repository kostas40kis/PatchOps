from __future__ import annotations

from dataclasses import asdict

from patchops.models import Manifest


def manifest_to_dict(manifest: Manifest) -> dict:
    return asdict(manifest)
