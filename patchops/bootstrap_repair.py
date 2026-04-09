from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class BootstrapRepairWriteRecord:
    relative_path: str
    source_path: Path
    target_path: Path
    backup_path: Path | None
    existed_before: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "existed_before": self.existed_before,
        }


@dataclass(frozen=True)
class BootstrapRepairValidationRecord:
    relative_path: str
    command: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str

    def to_dict(self) -> dict[str, object]:
        return {
            "relative_path": self.relative_path,
            "command": list(self.command),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "ok": self.exit_code == 0,
        }


@dataclass(frozen=True)
class BootstrapRepairResult:
    payload_root: Path
    target_root: Path
    backup_root: Path
    restored_paths: tuple[str, ...]
    write_records: tuple[BootstrapRepairWriteRecord, ...]
    validation_records: tuple[BootstrapRepairValidationRecord, ...]
    ok: bool
    issues: tuple[str, ...]
    next_action: str = "Return to the normal PatchOps workflow as soon as bootability is restored."

    def to_dict(self) -> dict[str, object]:
        return {
            "payload_root": str(self.payload_root),
            "target_root": str(self.target_root),
            "backup_root": str(self.backup_root),
            "restored_paths": list(self.restored_paths),
            "write_records": [item.to_dict() for item in self.write_records],
            "validation_records": [item.to_dict() for item in self.validation_records],
            "ok": self.ok,
            "issue_count": len(self.issues),
            "issues": list(self.issues),
            "next_action": self.next_action,
        }


def _normalize_relative_path(value: str | Path) -> str:
    text = str(value or "").replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    if not text:
        raise ValueError("Relative path must not be empty.")
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Bootstrap repair paths must stay relative and within the target root: {value}")
    return "/".join(path.parts)


def _default_backup_root(target_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return target_root / "data" / "runtime" / "bootstrap_repairs" / f"bootstrap_repair_{timestamp}" / "backups"


def _capture_py_compile(target_root: Path, relative_path: str) -> BootstrapRepairValidationRecord:
    target_path = target_root / Path(relative_path)
    command = (sys.executable, "-m", "py_compile", str(target_path))
    completed = subprocess.run(
        command,
        cwd=target_root,
        text=True,
        capture_output=True,
    )
    return BootstrapRepairValidationRecord(
        relative_path=relative_path,
        command=command,
        exit_code=int(completed.returncode),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def apply_bootstrap_repair(
    payload_root: str | Path,
    target_root: str | Path,
    relative_paths: list[str] | tuple[str, ...],
    *,
    backup_root: str | Path | None = None,
    py_compile_paths: list[str] | tuple[str, ...] | None = None,
) -> BootstrapRepairResult:
    payload_root = Path(payload_root).resolve()
    target_root = Path(target_root).resolve()
    normalized_paths = tuple(_normalize_relative_path(item) for item in (relative_paths or ()))
    if not normalized_paths:
        raise ValueError("Bootstrap repair requires at least one --path entry.")
    normalized_compile_paths = tuple(_normalize_relative_path(item) for item in (py_compile_paths or ()))

    if not payload_root.exists():
        raise FileNotFoundError(f"Bootstrap repair payload root does not exist: {payload_root}")
    if not target_root.exists():
        raise FileNotFoundError(f"Bootstrap repair target root does not exist: {target_root}")

    backup_root = Path(backup_root).resolve() if backup_root else _default_backup_root(target_root)
    backup_root.mkdir(parents=True, exist_ok=True)

    write_records: list[BootstrapRepairWriteRecord] = []
    for relative_path in normalized_paths:
        source_path = payload_root / Path(relative_path)
        target_path = target_root / Path(relative_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Bootstrap repair source file does not exist: {source_path}")
        if source_path.is_dir():
            raise IsADirectoryError(f"Bootstrap repair source path must be a file: {source_path}")

        backup_path: Path | None = None
        existed_before = target_path.exists()
        if existed_before:
            backup_path = backup_root / Path(relative_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target_path, backup_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        write_records.append(
            BootstrapRepairWriteRecord(
                relative_path=relative_path,
                source_path=source_path,
                target_path=target_path,
                backup_path=backup_path,
                existed_before=existed_before,
            )
        )

    validation_records = [
        _capture_py_compile(target_root, relative_path)
        for relative_path in normalized_compile_paths
    ]

    issues: list[str] = []
    for record in validation_records:
        if record.exit_code != 0:
            issues.append(
                f"py_compile failed for {record.relative_path} with exit code {record.exit_code}."
            )

    return BootstrapRepairResult(
        payload_root=payload_root,
        target_root=target_root,
        backup_root=backup_root,
        restored_paths=normalized_paths,
        write_records=tuple(write_records),
        validation_records=tuple(validation_records),
        ok=(len(issues) == 0),
        issues=tuple(issues),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchops.bootstrap_repair",
        description=(
            "normal PatchOps CLI import chain is too broken: apply a narrow bootstrap recovery payload."
        ),
    )
    parser.add_argument(
        "payload_root",
        help="Directory containing replacement files in target-relative shape.",
    )
    parser.add_argument(
        "--target-root",
        default=".",
        help="Target project root to repair. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--path",
        action="append",
        required=True,
        help="Relative file path to restore from the payload root. May be supplied more than once.",
    )
    parser.add_argument(
        "--py-compile-path",
        action="append",
        default=[],
        help="Relative Python file path to validate with py_compile after restore. May be supplied more than once.",
    )
    parser.add_argument(
        "--backup-root",
        default=None,
        help="Optional explicit backup root. Defaults under target_root/data/runtime/bootstrap_repairs/.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = apply_bootstrap_repair(
            args.payload_root,
            args.target_root,
            list(args.path or []),
            backup_root=args.backup_root,
            py_compile_paths=list(args.py_compile_path or []),
        )
    except Exception as exc:  # pragma: no cover - exercised through CLI contract tests
        payload = {
            "payload_root": str(Path(args.payload_root).resolve()),
            "target_root": str(Path(args.target_root).resolve()),
            "ok": False,
            "issue_count": 1,
            "issues": [str(exc)],
            "next_action": "Repair the bootstrap payload or target path, then rerun the narrow recovery helper.",
        }
        print(json.dumps(payload, indent=2))
        return 1

    payload = result.to_dict()
    print(json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
