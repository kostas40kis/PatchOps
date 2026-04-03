from __future__ import annotations

from pathlib import Path

from patchops.models import Manifest
from patchops.profiles.base import resolve_profile


PLACEHOLDER_PATH = "relative/path/to/file.ext"


def _render_path(value: Path | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _stub_manifest(profile_name: str) -> Manifest:
    return Manifest(
        manifest_version="1",
        patch_name="template_patch",
        active_profile=profile_name,
    )


def _starter_validation(use_profile_runtime: bool) -> dict:
    return {
        "name": "validation_command",
        "program": "python",
        "args": ["-m", "pytest", "-q"],
        "working_directory": ".",
        "use_profile_runtime": use_profile_runtime,
        "allowed_exit_codes": [0],
    }


def build_manifest_template(
    profile_name: str,
    wrapper_project_root: str | Path | None = None,
    mode: str = "apply",
    patch_name: str = "template_patch",
    target_root: str | None = None,
) -> dict:
    wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root else Path(__file__).resolve().parents[1]
    manifest = _stub_manifest(profile_name)
    resolved_profile = resolve_profile(manifest, wrapper_root)

    effective_target_root = target_root if target_root is not None else _render_path(resolved_profile.default_target_root)
    use_profile_runtime = resolved_profile.runtime_path is not None

    payload = {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": resolved_profile.name,
        "target_project_root": effective_target_root,
        "backup_files": [PLACEHOLDER_PATH],
        "files_to_write": [],
        "validation_commands": [_starter_validation(use_profile_runtime)],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": None,
            "report_name_prefix": None,
            "write_to_desktop": True,
        },
        "tags": ["template", resolved_profile.name, mode],
        "notes": "Replace placeholder paths, content, and commands before using this manifest for real work.",
    }

    if mode == "apply":
        payload["files_to_write"] = [
            {
                "path": PLACEHOLDER_PATH,
                "content": "REPLACE_ME\n",
                "content_path": None,
                "encoding": resolved_profile.encoding,
            }
        ]

    return payload