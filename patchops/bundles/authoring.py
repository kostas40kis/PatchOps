from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import tempfile
import zipfile

from .launcher_emitter import METADATA_DRIVEN_LAUNCHER_MODE, emit_root_bundle_launcher
from .launcher_self_check import check_launcher_path
from .shape_validation import BundleShapeIssue, validate_bundle_directory, validate_bundle_zip

BundleValidationMessage = BundleShapeIssue
VALID_BUNDLE_MODES = ("apply", "verify", "proof")
VALID_PROOF_BUNDLE_KINDS = ("apply", "verify", "launcher-risk")


@dataclass(frozen=True)
class BundleExecutionMetadata:
    bundle_root: Path
    bundle_mode: str
    manifest_path: Path
    content_root: Path
    recommended_profile: str
    launcher_path: Path


@dataclass(frozen=True)
class BundleExecutionEntryResult:
    bundle_root: Path
    manifest_path: Path
    workflow_mode: str
    wrapper_root: str | None
    delegated_commands: tuple[tuple[str, ...], ...]
    executed_command_count: int
    exit_code: int

    def to_dict(self) -> dict:
        return {
            "bundle_root": str(self.bundle_root),
            "manifest_path": str(self.manifest_path),
            "workflow_mode": self.workflow_mode,
            "wrapper_root": self.wrapper_root,
            "delegated_commands": [list(command) for command in self.delegated_commands],
            "executed_command_count": self.executed_command_count,
            "exit_code": self.exit_code,
            "ok": self.exit_code == 0,
        }


@dataclass(frozen=True)
class BundleAuthoringResult:
    bundle_root: Path
    manifest_path: Path
    bundle_meta_path: Path
    readme_path: Path
    launcher_path: Path
    content_root: Path


@dataclass(frozen=True)
class BundleProofBundleResult:
    kind: str
    bundle_root: Path
    manifest_path: Path
    bundle_meta_path: Path
    readme_path: Path
    launcher_path: Path
    content_root: Path
    proof_file_path: Path
    bundle_mode: str
    intended_surface: str
    expected_exit_code: int
    ok: bool
    issue_count: int
    issues: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "bundle_root": str(self.bundle_root),
            "manifest_path": str(self.manifest_path),
            "bundle_meta_path": str(self.bundle_meta_path),
            "readme_path": str(self.readme_path),
            "launcher_path": str(self.launcher_path),
            "content_root": str(self.content_root),
            "proof_file_path": str(self.proof_file_path),
            "bundle_mode": self.bundle_mode,
            "intended_surface": self.intended_surface,
            "expected_exit_code": self.expected_exit_code,
            "ok": self.ok,
            "issue_count": self.issue_count,
            "issues": list(self.issues),
        }


@dataclass(frozen=True)
class BundleAuthoringSelfCheckResult:
    bundle_root: Path
    shape_messages: tuple[BundleValidationMessage, ...]
    launcher_messages: tuple[BundleValidationMessage, ...]

    @property
    def messages(self) -> tuple[BundleValidationMessage, ...]:
        return self.shape_messages + self.launcher_messages

    @property
    def issue_count(self) -> int:
        return len(self.messages)

    @property
    def is_valid(self) -> bool:
        return self.issue_count == 0


@dataclass(frozen=True)
class BundleBuildResult:
    bundle_root: Path
    output_zip: Path
    root_folder_name: str
    member_count: int
    issues: tuple[BundleValidationMessage, ...]

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


@dataclass(frozen=True)
class BundleDoctorResult:
    source_path: Path
    source_kind: str
    ok: bool
    issue_count: int
    shape_issue_count: int
    launcher_issue_count: int
    build_issue_count: int
    issues: tuple[BundleValidationMessage, ...]
    root_folder_name: str | None = None
    manifest_path: str | None = None
    bundle_meta_path: str | None = None
    content_root_path: str | None = None
    launcher_paths: tuple[str, ...] = ()
    build_output_zip: str | None = None
    summary_lines: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "source_path": str(self.source_path),
            "source_kind": self.source_kind,
            "ok": self.ok,
            "issue_count": self.issue_count,
            "shape_issue_count": self.shape_issue_count,
            "launcher_issue_count": self.launcher_issue_count,
            "build_issue_count": self.build_issue_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "root_folder_name": self.root_folder_name,
            "manifest_path": self.manifest_path,
            "bundle_meta_path": self.bundle_meta_path,
            "content_root_path": self.content_root_path,
            "launcher_paths": list(self.launcher_paths),
            "build_output_zip": self.build_output_zip,
            "summary_lines": list(self.summary_lines),
            "summary_text": "\n".join(self.summary_lines),
        }


def _normalize_bundle_mode(mode: str) -> str:
    normalized = str(mode or "apply").strip().lower()
    if normalized not in VALID_BUNDLE_MODES:
        allowed = ", ".join(VALID_BUNDLE_MODES)
        raise ValueError(f"Unsupported bundle mode '{mode}'. Expected one of: {allowed}")
    return normalized



def create_starter_bundle(
    bundle_root: str | Path,
    *,
    patch_name: str,
    target_project: str,
    target_project_root: str,
    wrapper_project_root: str = r"C:\dev\patchops",
    recommended_profile: str = "generic_python",
    mode: str = "apply",
) -> BundleAuthoringResult:
    normalized_mode = _normalize_bundle_mode(mode)

    root = Path(bundle_root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    content_root = root / "content"
    content_root.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "manifest.json"
    bundle_meta_path = root / "bundle_meta.json"
    readme_path = root / "README.txt"
    launcher_path = root / "run_with_patchops.ps1"

    manifest = {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": recommended_profile,
        "target_project_root": target_project_root,
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": None,
            "report_name_prefix": patch_name,
            "write_to_desktop": True,
        },
        "tags": [
            "bundle",
            "starter",
            "python_owned_authoring",
        ],
        "notes": "Starter bundle generated by PatchOps Python bundle authoring helper.",
    }

    bundle_meta = {
        "bundle_schema_version": 1,
        "patch_name": patch_name,
        "target_project": target_project,
        "recommended_profile": recommended_profile,
        "target_project_root": target_project_root,
        "wrapper_project_root": wrapper_project_root,
        "content_root": "content",
        "manifest_path": "manifest.json",
        "launcher_path": "run_with_patchops.ps1",
        "bundle_mode": normalized_mode,
    }

    readme = f"""PatchOps starter bundle
======================

Patch name : {patch_name}
Target     : {target_project}
Profile    : {recommended_profile}
Mode       : {normalized_mode}

This starter bundle was generated by the Python bundle authoring helper.

Bundle root files
- manifest.json
- bundle_meta.json
- README.txt
- run_with_patchops.ps1
- content/

Launcher generation rule
- do not hand-author the saved root launcher unless you are repairing it deliberately
- let PatchOps emit the saved launcher in the normal script-file form
- keep inline `& {{ ... }}` wrapping for paste-safe or generated inline scenarios only when needed

Starter workflow
1. Run `py -m patchops.cli make-bundle <bundle-root> --mode {normalized_mode}`.
2. Put staged target files under `content/` using target-relative paths.
3. Fill `manifest.json` files_to_write and validation_commands.
4. Run `py -m patchops.cli check-bundle <bundle-root>` before packaging.
5. Build the zip only after the bundle root passes the self-check gate.

Mode note
- `bundle_mode` now drives apply vs verify behavior from metadata.
- the root launcher shape stays the same for apply, verify, and proof bundles.
- `proof` mode keeps proof metadata but resolves to the apply workflow through metadata.
"""

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bundle_meta_path.write_text(json.dumps(bundle_meta, indent=2) + "\n", encoding="utf-8")
    readme_path.write_text(readme, encoding="utf-8")

    emit_result = emit_root_bundle_launcher(
        launcher_path,
        wrapper_project_root=wrapper_project_root,
        mode=METADATA_DRIVEN_LAUNCHER_MODE,
    )
    if not emit_result.ok:
        joined = "\n".join(emit_result.issues) if emit_result.issues else "(no issues reported)"
        raise ValueError(f"Generated launcher failed self-check:\n{joined}")

    return BundleAuthoringResult(
        bundle_root=root,
        manifest_path=manifest_path,
        bundle_meta_path=bundle_meta_path,
        readme_path=readme_path,
        launcher_path=launcher_path,
        content_root=content_root,
    )



def _normalize_proof_bundle_kind(kind: str) -> str:
    normalized = str(kind or "apply").strip().lower()
    if normalized not in VALID_PROOF_BUNDLE_KINDS:
        allowed = ", ".join(VALID_PROOF_BUNDLE_KINDS)
        raise ValueError(f"Unsupported proof bundle kind '{kind}'. Expected one of: {allowed}")
    return normalized


def _write_json_file(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _append_unique_tags(existing: Sequence[str], *tags: str) -> list[str]:
    ordered: list[str] = []
    for value in [*existing, *tags]:
        cleaned = str(value).strip()
        if cleaned and cleaned not in ordered:
            ordered.append(cleaned)
    return ordered


def _configure_manifest_for_single_content_file(
    manifest_path: Path,
    *,
    patch_name: str,
    target_path: str,
    content_path: str,
    proof_kind: str,
) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Starter manifest must contain a JSON object.")
    manifest["files_to_write"] = [
        {
            "path": target_path,
            "content_path": content_path,
            "encoding": "utf-8",
        }
    ]
    manifest["validation_commands"] = []
    manifest["smoke_commands"] = []
    manifest["audit_commands"] = []
    manifest["cleanup_commands"] = []
    manifest["archive_commands"] = []
    manifest["tags"] = _append_unique_tags(manifest.get("tags") or [], "proof-bundle", proof_kind)
    manifest["notes"] = (
        f"Proof bundle generated by PatchOps for the {proof_kind} surface. "
        f"Patch name: {patch_name}."
    )
    _write_json_file(manifest_path, manifest)


def _configure_bundle_meta_for_proof_kind(
    bundle_meta_path: Path,
    *,
    proof_kind: str,
    bundle_mode: str,
) -> None:
    bundle_meta = json.loads(bundle_meta_path.read_text(encoding="utf-8"))
    if not isinstance(bundle_meta, dict):
        raise ValueError("Starter bundle metadata must contain a JSON object.")
    bundle_meta["bundle_mode"] = bundle_mode
    bundle_meta["proof_bundle_kind"] = proof_kind
    _write_json_file(bundle_meta_path, bundle_meta)


def create_proof_bundle(
    bundle_root: str | Path,
    *,
    kind: str,
    patch_name: str,
    target_project: str,
    target_project_root: str,
    wrapper_project_root: str = r"C:\dev\patchops",
    recommended_profile: str = "generic_python",
) -> BundleProofBundleResult:
    normalized_kind = _normalize_proof_bundle_kind(kind)
    bundle_mode = "verify" if normalized_kind == "verify" else "apply"

    starter = create_starter_bundle(
        bundle_root,
        patch_name=patch_name,
        target_project=target_project,
        target_project_root=target_project_root,
        wrapper_project_root=wrapper_project_root,
        recommended_profile=recommended_profile,
        mode=bundle_mode,
    )

    proof_stem = normalized_kind.replace("-", "_")
    proof_file_path = starter.content_root / "docs" / f"{proof_stem}_proof_bundle.md"
    proof_file_path.parent.mkdir(parents=True, exist_ok=True)
    proof_file_path.write_text(
        f"# {patch_name}\n\n"
        f"Generated PatchOps proof bundle for the {normalized_kind} surface.\n",
        encoding="utf-8",
    )

    _configure_manifest_for_single_content_file(
        starter.manifest_path,
        patch_name=patch_name,
        target_path=f"docs/{proof_stem}_proof_bundle.md",
        content_path=f"content/docs/{proof_stem}_proof_bundle.md",
        proof_kind=normalized_kind,
    )
    _configure_bundle_meta_for_proof_kind(
        starter.bundle_meta_path,
        proof_kind=normalized_kind,
        bundle_mode=bundle_mode,
    )

    intended_surface = "run-package"
    expected_exit_code = 0

    if normalized_kind == "launcher-risk":
        starter.launcher_path.write_text(
            "& {\n"
            "    Get-Content prep.json | ConvertFrom-Json\n"
            "    py -c \"print('inline')\"\n"
            "}\n",
            encoding="utf-8",
        )
        intended_surface = "bundle-doctor"
        expected_exit_code = 1

    return BundleProofBundleResult(
        kind=normalized_kind,
        bundle_root=starter.bundle_root,
        manifest_path=starter.manifest_path,
        bundle_meta_path=starter.bundle_meta_path,
        readme_path=starter.readme_path,
        launcher_path=starter.launcher_path,
        content_root=starter.content_root,
        proof_file_path=proof_file_path,
        bundle_mode=bundle_mode,
        intended_surface=intended_surface,
        expected_exit_code=expected_exit_code,
        ok=True,
        issue_count=0,
        issues=(),
    )



def resolve_bundle_execution_metadata(bundle_root: str | Path) -> BundleExecutionMetadata:
    root = Path(bundle_root).resolve()
    bundle_meta_path = root / "bundle_meta.json"
    if not bundle_meta_path.is_file():
        raise FileNotFoundError(f"bundle_meta.json not found under bundle root: {root}")

    payload = json.loads(bundle_meta_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("bundle_meta.json must contain a JSON object.")

    bundle_mode = _normalize_bundle_mode(payload.get("bundle_mode") or "apply")
    manifest_relative = str(payload.get("manifest_path") or "manifest.json")
    content_relative = str(payload.get("content_root") or "content")
    launcher_relative = str(payload.get("launcher_path") or "run_with_patchops.ps1")
    recommended_profile = str(payload.get("recommended_profile") or "generic_python")

    return BundleExecutionMetadata(
        bundle_root=root,
        bundle_mode=bundle_mode,
        manifest_path=(root / Path(manifest_relative)).resolve(),
        content_root=(root / Path(content_relative)).resolve(),
        recommended_profile=recommended_profile,
        launcher_path=(root / Path(launcher_relative)).resolve(),
    )


def resolve_bundle_workflow_mode(bundle_root_or_metadata: str | Path | BundleExecutionMetadata) -> str:
    metadata = (
        bundle_root_or_metadata
        if isinstance(bundle_root_or_metadata, BundleExecutionMetadata)
        else resolve_bundle_execution_metadata(bundle_root_or_metadata)
    )
    return "verify" if metadata.bundle_mode == "verify" else "apply"

def run_bundle_execution_entry(
    bundle_root: str | Path,
    *,
    wrapper_root: str | None = None,
    command_runner: Callable[[list[str]], int] | None = None,
) -> BundleExecutionEntryResult:
    metadata = resolve_bundle_execution_metadata(bundle_root)
    workflow_mode = resolve_bundle_workflow_mode(metadata)
    normalized_wrapper_root = str(Path(wrapper_root).resolve()) if wrapper_root else None

    commands: list[list[str]] = [
        ["check-bundle", str(metadata.bundle_root)],
        ["check", str(metadata.manifest_path)],
        ["inspect", str(metadata.manifest_path)],
        ["plan", str(metadata.manifest_path)],
    ]
    final_command = [workflow_mode, str(metadata.manifest_path)]
    if normalized_wrapper_root:
        final_command.extend(["--wrapper-root", normalized_wrapper_root])
    commands.append(final_command)

    runner = command_runner
    if runner is None:
        from patchops.cli import main as cli_main
        runner = cli_main

    executed_count = 0
    exit_code = 0
    for nested_argv in commands:
        executed_count += 1
        exit_code = int(runner(list(nested_argv)))
        if exit_code != 0:
            break

    return BundleExecutionEntryResult(
        bundle_root=metadata.bundle_root,
        manifest_path=metadata.manifest_path,
        workflow_mode=workflow_mode,
        wrapper_root=normalized_wrapper_root,
        delegated_commands=tuple(tuple(command) for command in commands),
        executed_command_count=executed_count,
        exit_code=exit_code,
    )


def _collect_manifest_content_path_messages(bundle_root: Path, manifest_path: Path) -> tuple[BundleValidationMessage, ...]:
    if not manifest_path.is_file():
        return ()

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return (
            BundleValidationMessage(
                code="manifest_json_invalid",
                message="Bundle manifest is not valid JSON.",
                path=str(manifest_path),
            ),
        )

    files_to_write = manifest.get("files_to_write") or []
    if not isinstance(files_to_write, list):
        return (
            BundleValidationMessage(
                code="files_to_write_invalid",
                message="Bundle manifest files_to_write must be a list.",
                path=str(manifest_path),
            ),
        )

    messages: list[BundleValidationMessage] = []
    for entry in files_to_write:
        if not isinstance(entry, dict):
            continue
        content_path = entry.get("content_path")
        if not content_path:
            continue
        candidate = bundle_root / Path(str(content_path))
        if not candidate.is_file():
            messages.append(
                BundleValidationMessage(
                    code="content_path_missing",
                    message=f"Bundle content_path entry does not exist: {content_path}",
                    path=str(candidate),
                )
            )
    return tuple(messages)


def run_bundle_authoring_self_check(
    bundle_root: str | Path,
    *,
    launcher_checker: Callable[[Path], Sequence[BundleValidationMessage]] | None = None,
) -> BundleAuthoringSelfCheckResult:
    root = Path(bundle_root).resolve()
    shape_result = validate_bundle_directory(root)
    shape_messages = tuple(shape_result.issues) + _collect_manifest_content_path_messages(root, root / "manifest.json")

    launcher_messages: tuple[BundleValidationMessage, ...] = ()
    launcher_path = root / "run_with_patchops.ps1"
    if launcher_checker is not None and launcher_path.is_file():
        launcher_messages = tuple(launcher_checker(launcher_path))

    return BundleAuthoringSelfCheckResult(
        bundle_root=root,
        shape_messages=shape_messages,
        launcher_messages=launcher_messages,
    )


def _build_issue(*, code: str, message: str, path: str | None = None) -> BundleValidationMessage:
    return BundleValidationMessage(code=code, message=message, path=path)


def _iter_bundle_files(bundle_root: Path) -> list[Path]:
    return sorted(
        (path for path in bundle_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(bundle_root).as_posix(),
    )


def _deterministic_zipinfo(archive_name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(archive_name)
    info.date_time = (2020, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def build_bundle_zip(bundle_root: str | Path, output_zip: str | Path) -> BundleBuildResult:
    root = Path(bundle_root).resolve()
    output = Path(output_zip).resolve()

    self_check = run_bundle_authoring_self_check(root)
    early_issues = list(self_check.messages)

    if output.suffix.lower() != ".zip":
        early_issues.append(
            _build_issue(
                code="output_not_zip",
                message="Bundle build output must use a .zip path.",
                path=str(output),
            )
        )

    if output.exists() and output.is_dir():
        early_issues.append(
            _build_issue(
                code="output_path_is_directory",
                message="Bundle build output path points to a directory, not a zip file.",
                path=str(output),
            )
        )

    content_root = root / "content"
    content_files = sorted(path for path in content_root.rglob("*") if path.is_file()) if content_root.exists() else []
    if not content_files:
        early_issues.append(
            _build_issue(
                code="content_root_empty",
                message="Bundle content/ root must contain at least one file before zip creation.",
                path=str(content_root),
            )
        )

    if early_issues:
        return BundleBuildResult(
            bundle_root=root,
            output_zip=output,
            root_folder_name=root.name,
            member_count=0,
            issues=tuple(early_issues),
        )

    file_paths = _iter_bundle_files(root)
    if not file_paths:
        return BundleBuildResult(
            bundle_root=root,
            output_zip=output,
            root_folder_name=root.name,
            member_count=0,
            issues=(
                _build_issue(
                    code="bundle_has_no_files",
                    message="Bundle root does not contain any files to archive.",
                    path=str(root),
                ),
            ),
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in file_paths:
            relative_path = path.relative_to(root).as_posix()
            archive_name = f"{root.name}/{relative_path}"
            archive.writestr(_deterministic_zipinfo(archive_name), path.read_bytes())

    zip_result = validate_bundle_zip(output)
    return BundleBuildResult(
        bundle_root=root,
        output_zip=output,
        root_folder_name=root.name,
        member_count=len(file_paths),
        issues=tuple(zip_result.issues),
    )

def _launcher_payload_to_messages(payload: dict, *, path: Path) -> tuple[BundleValidationMessage, ...]:
    messages: list[BundleValidationMessage] = []
    for index, item in enumerate(payload.get("issues") or [], start=1):
        messages.append(
            _build_issue(
                code=f"launcher_risk_{index}",
                message=str(item),
                path=str(path),
            )
        )
    return tuple(messages)


def _dedupe_messages(messages: Sequence[BundleValidationMessage]) -> tuple[BundleValidationMessage, ...]:
    seen: set[tuple[str, str, str | None]] = set()
    ordered: list[BundleValidationMessage] = []
    for message in messages:
        key = (message.code, message.message, message.path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(message)
    return tuple(ordered)


def _launcher_paths_for_directory(root: Path) -> tuple[str, ...]:
    launcher_path = root / "run_with_patchops.ps1"
    if launcher_path.is_file():
        return (launcher_path.relative_to(root).as_posix(),)
    return ()


def run_bundle_doctor(bundle_root_or_zip: str | Path) -> BundleDoctorResult:
    source = Path(bundle_root_or_zip).resolve()

    if source.suffix.lower() == ".zip":
        shape_result = validate_bundle_zip(source)
        launcher_messages: tuple[BundleValidationMessage, ...] = ()

        if shape_result.ok and len(shape_result.launcher_paths) == 1:
            with tempfile.TemporaryDirectory(prefix="patchops_bundle_doctor_") as temp_dir:
                with zipfile.ZipFile(source, "r") as archive:
                    archive.extractall(temp_dir)
                launcher_path = Path(temp_dir) / shape_result.launcher_paths[0]
                launcher_payload = check_launcher_path(launcher_path)
                launcher_messages = _launcher_payload_to_messages(launcher_payload, path=launcher_path)

        issues = _dedupe_messages(tuple(shape_result.issues) + launcher_messages)
        summary_lines = (
            f"Bundle doctor source : {source}",
            "Source kind          : zip",
            f"Shape issues         : {len(shape_result.issues)}",
            f"Launcher issues      : {len(launcher_messages)}",
            "Build verification   : already-built zip; export shape reviewed directly",
            f"Overall result       : {'PASS' if len(issues) == 0 else 'FAIL'}",
        )
        return BundleDoctorResult(
            source_path=source,
            source_kind="zip",
            ok=len(issues) == 0,
            issue_count=len(issues),
            shape_issue_count=len(shape_result.issues),
            launcher_issue_count=len(launcher_messages),
            build_issue_count=0,
            issues=issues,
            root_folder_name=shape_result.root_folder_name,
            manifest_path=shape_result.manifest_path,
            bundle_meta_path=shape_result.bundle_meta_path,
            content_root_path=shape_result.content_root_path,
            launcher_paths=tuple(shape_result.launcher_paths),
            build_output_zip=None,
            summary_lines=summary_lines,
        )

    self_check = run_bundle_authoring_self_check(source, launcher_checker=lambda path: _launcher_payload_to_messages(check_launcher_path(path), path=path))

    build_issues: tuple[BundleValidationMessage, ...] = ()
    build_output_zip: str | None = None
    with tempfile.TemporaryDirectory(prefix="patchops_bundle_doctor_build_") as temp_dir:
        temp_zip = Path(temp_dir) / f"{source.name}.zip"
        build_result = build_bundle_zip(source, temp_zip)
        build_issues = tuple(build_result.issues)
        if build_result.ok:
            build_output_zip = None

    issues = _dedupe_messages(tuple(self_check.messages) + build_issues)
    summary_lines = (
        f"Bundle doctor source : {source}",
        "Source kind          : directory",
        f"Shape issues         : {len(self_check.shape_messages)}",
        f"Launcher issues      : {len(self_check.launcher_messages)}",
        f"Build verification   : {'PASS' if len(build_issues) == 0 else 'FAIL'}",
        f"Overall result       : {'PASS' if len(issues) == 0 else 'FAIL'}",
    )
    return BundleDoctorResult(
        source_path=source,
        source_kind="directory",
        ok=len(issues) == 0,
        issue_count=len(issues),
        shape_issue_count=len(self_check.shape_messages),
        launcher_issue_count=len(self_check.launcher_messages),
        build_issue_count=len(build_issues),
        issues=issues,
        root_folder_name=source.name if source.exists() else None,
        manifest_path=str(source / "manifest.json") if (source / "manifest.json").exists() else None,
        bundle_meta_path=str(source / "bundle_meta.json") if (source / "bundle_meta.json").exists() else None,
        content_root_path=str(source / "content") if (source / "content").exists() else None,
        launcher_paths=_launcher_paths_for_directory(source),
        build_output_zip=build_output_zip,
        summary_lines=summary_lines,
    )




__all__ = [
    "BundleAuthoringResult",
    "BundleAuthoringSelfCheckResult",
    "BundleBuildResult",
    "BundleDoctorResult",
    "BundleProofBundleResult",
    "BundleExecutionEntryResult",
    "BundleExecutionMetadata",
    "BundleValidationMessage",
    "VALID_BUNDLE_MODES",
    "VALID_PROOF_BUNDLE_KINDS",
    "build_bundle_zip",
    "create_proof_bundle",
    "run_bundle_doctor",
    "create_starter_bundle",
    "resolve_bundle_execution_metadata",
    "resolve_bundle_workflow_mode",
    "run_bundle_authoring_self_check",
    "run_bundle_execution_entry",
]
