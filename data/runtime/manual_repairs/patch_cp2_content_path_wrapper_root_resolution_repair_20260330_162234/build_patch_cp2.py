from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
patch_root = Path(sys.argv[2]).resolve()
desktop = Path(sys.argv[3]).resolve()
patch_name = sys.argv[4]
validation_program = sys.argv[5]
validation_args_path = Path(sys.argv[6]).resolve()
validation_args = json.loads(validation_args_path.read_text(encoding="utf-8"))

writers_path = project_root / "patchops/files/writers.py"
apply_patch_path = project_root / "patchops/workflows/apply_patch.py"
test_writers_path = project_root / "tests/test_writers.py"

current_apply_patch = apply_patch_path.read_text(encoding="utf-8")
old_call = "content = load_content(spec, manifest_path=manifest_path)"
new_call = "content = load_content(spec, manifest_path=manifest_path, wrapper_project_root=wrapper_root)"
if old_call not in current_apply_patch:
    raise RuntimeError("Expected load_content call not found in patchops/workflows/apply_patch.py")

updated_apply_patch = current_apply_patch.replace(old_call, new_call, 1)

writers_content = textwrap.dedent(
    """
    from __future__ import annotations

    from pathlib import Path

    from patchops.files.paths import ensure_directory
    from patchops.models import FileWriteSpec, WriteRecord


    def load_content(
        spec: FileWriteSpec,
        manifest_path: Path | None = None,
        wrapper_project_root: Path | None = None,
    ) -> str:
        if spec.content is not None:
            return spec.content
        if spec.content_path is None:
            raise ValueError(f"No content source defined for {spec.path}")

        content_path = Path(spec.content_path)
        if not content_path.is_absolute():
            candidate_paths: list[Path] = []
            if wrapper_project_root is not None:
                candidate_paths.append(Path(wrapper_project_root) / content_path)
            if manifest_path is not None:
                candidate_paths.append(Path(manifest_path).parent / content_path)

            if candidate_paths:
                for candidate in candidate_paths:
                    if candidate.exists():
                        content_path = candidate
                        break
                else:
                    content_path = candidate_paths[0]

        return content_path.read_text(encoding=spec.encoding)


    def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:
        ensure_directory(destination.parent)
        destination.write_text(content, encoding=encoding)
        return WriteRecord(path=destination, encoding=encoding)
    """
).lstrip()

test_writers_content = textwrap.dedent(
    """
    from pathlib import Path

    from patchops.files.writers import load_content, write_text_file
    from patchops.models import FileWriteSpec


    def test_write_text_file_creates_parent_dirs(tmp_path: Path):
        destination = tmp_path / "nested" / "a.txt"
        record = write_text_file(destination, "hello")
        assert destination.read_text(encoding="utf-8") == "hello"
        assert record.path == destination


    def test_load_content_prefers_wrapper_project_root_for_relative_content_path(tmp_path: Path):
        wrapper_root = tmp_path / "wrapper_root"
        manifest_dir = wrapper_root / "data" / "runtime" / "manual_repairs" / "sample_patch"
        manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = manifest_dir / "patch_manifest.json"
        manifest_path.write_text("{}", encoding="utf-8")

        relative_content_path = Path("content/source.txt")

        wrapper_source = wrapper_root / relative_content_path
        wrapper_source.parent.mkdir(parents=True, exist_ok=True)
        wrapper_source.write_text("wrapper-root payload\\n", encoding="utf-8")

        manifest_local_source = manifest_dir / relative_content_path
        manifest_local_source.parent.mkdir(parents=True, exist_ok=True)
        manifest_local_source.write_text("manifest-local payload\\n", encoding="utf-8")

        spec = FileWriteSpec(
            path="OUTPUT.txt",
            content=None,
            content_path=relative_content_path.as_posix(),
            encoding="utf-8",
        )

        content = load_content(
            spec,
            manifest_path=manifest_path,
            wrapper_project_root=wrapper_root,
        )

        assert content == "wrapper-root payload\\n"


    def test_load_content_falls_back_to_manifest_local_when_wrapper_root_file_is_missing(tmp_path: Path):
        wrapper_root = tmp_path / "wrapper_root"
        manifest_dir = wrapper_root / "data" / "runtime" / "manual_repairs" / "sample_patch"
        manifest_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = manifest_dir / "patch_manifest.json"
        manifest_path.write_text("{}", encoding="utf-8")

        relative_content_path = Path("content/source.txt")
        manifest_local_source = manifest_dir / relative_content_path
        manifest_local_source.parent.mkdir(parents=True, exist_ok=True)
        manifest_local_source.write_text("manifest-local payload\\n", encoding="utf-8")

        spec = FileWriteSpec(
            path="OUTPUT.txt",
            content=None,
            content_path=relative_content_path.as_posix(),
            encoding="utf-8",
        )

        content = load_content(
            spec,
            manifest_path=manifest_path,
            wrapper_project_root=wrapper_root,
        )

        assert content == "manifest-local payload\\n"
    """
).lstrip()

patch_root.mkdir(parents=True, exist_ok=True)

manifest = {
    "manifest_version": "1",
    "patch_name": patch_name,
    "active_profile": "generic_python",
    "target_project_root": project_root.as_posix(),
    "backup_files": [],
    "files_to_write": [
        {
            "path": "patchops/files/writers.py",
            "content": writers_content,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "patchops/workflows/apply_patch.py",
            "content": updated_apply_patch,
            "content_path": None,
            "encoding": "utf-8",
        },
        {
            "path": "tests/test_writers.py",
            "content": test_writers_content,
            "content_path": None,
            "encoding": "utf-8",
        },
    ],
    "validation_commands": [
        {
            "name": "pytest_content_path_resolution_repair",
            "program": validation_program,
            "args": validation_args,
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "smoke_commands": [],
    "audit_commands": [],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": desktop.as_posix(),
        "report_name_prefix": patch_name,
        "write_to_desktop": False,
    },
    "tags": ["content_path", "wrapper_relative", "resolver_repair", "current_state"],
    "notes": (
        "Second repair-stream patch. "
        "This patch repairs wrapper-root content_path resolution, preserves manifest-local fallback, "
        "and validates both flows."
    ),
}

manifest_path = patch_root / "patch_manifest.json"
# Write compact JSON (no extra whitespace, no trailing newline)
manifest_json = json.dumps(manifest, indent=None, separators=(',', ':'))
manifest_path.write_text(manifest_json, encoding="utf-8")

# Validate the manifest immediately
try:
    with manifest_path.open(encoding="utf-8") as f:
        json.load(f)
except Exception as e:
    raise RuntimeError(f"Manifest validation failed: {e}\nContent:\n{manifest_path.read_text(encoding='utf-8')}")

print(json.dumps({
    "manifest_path": str(manifest_path),
    "writers_path": str(writers_path),
    "apply_patch_path": str(apply_patch_path),
    "test_writers_path": str(test_writers_path),
}))