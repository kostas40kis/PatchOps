from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from types import SimpleNamespace

from patchops import package_runner


@dataclass
class DataclassPayload:
    ok: bool
    report_path: Path
    nested: dict[str, object]


class SlottedPayload:
    __slots__ = ("exit_code", "path")

    def __init__(self, exit_code: int, path: Path) -> None:
        self.exit_code = exit_code
        self.path = path


class FallbackResult:
    def __init__(self, report_path: Path) -> None:
        self.ok = True
        self.exit_code = 0
        self.report_path = report_path
        self.notes = ["fallback object should serialize"]


def test_run_package_result_serializer_handles_dataclass_dict_primitive_none_and_paths(tmp_path: Path) -> None:
    payload = DataclassPayload(
        ok=True,
        report_path=tmp_path / "outer.txt",
        nested={
            "none_value": None,
            "primitive": 7,
            "path": tmp_path / "inner.txt",
            "tuple": ("x", tmp_path / "tuple.txt"),
            "namespace": SimpleNamespace(answer=42, path=tmp_path / "namespace.txt"),
            "slots": SlottedPayload(0, tmp_path / "slotted.txt"),
        },
    )

    data = package_runner._run_package_result_to_jsonable(payload)

    assert data["ok"] is True
    assert data["report_path"] == str(tmp_path / "outer.txt")
    assert data["nested"]["none_value"] is None
    assert data["nested"]["primitive"] == 7
    assert data["nested"]["path"] == str(tmp_path / "inner.txt")
    assert data["nested"]["tuple"] == ["x", str(tmp_path / "tuple.txt")]
    assert data["nested"]["namespace"]["answer"] == 42
    assert data["nested"]["namespace"]["path"] == str(tmp_path / "namespace.txt")
    assert data["nested"]["slots"]["exit_code"] == 0
    assert data["nested"]["slots"]["path"] == str(tmp_path / "slotted.txt")

    json.dumps(data)


def test_run_package_cli_main_uses_safe_serializer_for_fallback_result_objects(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_run_delivery_package(*args, **kwargs):
        return FallbackResult(tmp_path / "outer.txt")

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            str(tmp_path / "bundle.zip"),
            "--wrapper-root",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert exit_code == 0
    assert data["ok"] is True
    assert data["exit_code"] == 0
    assert data["report_path"] == str(tmp_path / "outer.txt")
    assert data["notes"] == ["fallback object should serialize"]


def test_run_package_cli_main_uses_safe_serializer_for_dict_result(monkeypatch, capsys, tmp_path: Path) -> None:
    def fake_run_delivery_package(*args, **kwargs):
        return {
            "ok": True,
            "exit_code": 0,
            "report_path": tmp_path / "dict-report.txt",
            "nested": {"path": tmp_path / "nested.txt"},
        }

    monkeypatch.setattr(package_runner, "run_delivery_package", fake_run_delivery_package)

    exit_code = package_runner.cli_main(
        [
            str(tmp_path / "bundle.zip"),
            "--wrapper-root",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert exit_code == 0
    assert data["ok"] is True
    assert data["report_path"] == str(tmp_path / "dict-report.txt")
    assert data["nested"]["path"] == str(tmp_path / "nested.txt")
