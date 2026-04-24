from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
import re

import patchops.package_runner as package_runner


class DemoKind(Enum):
    OK = "ok"


@dataclass(slots=True)
class DemoResult:
    exit_code: int
    report_path: Path
    kind: DemoKind


def test_dataclass_result_serializes_without_type_error(tmp_path: Path) -> None:
    payload = package_runner._json_safe_result(
        DemoResult(exit_code=7, report_path=tmp_path / "report.txt", kind=DemoKind.OK)
    )

    encoded = json.dumps(payload, indent=2, default=str)
    loaded = json.loads(encoded)

    assert loaded["exit_code"] == 7
    assert loaded["report_path"].endswith("report.txt")
    assert loaded["kind"] == "ok"


def test_dict_result_serializes_and_normalizes_nested_paths(tmp_path: Path) -> None:
    payload = package_runner._json_safe_result(
        {
            "exit_code": 3,
            "report_path": tmp_path / "outer.txt",
            "nested": {"paths": [tmp_path / "a.txt", tmp_path / "b.txt"]},
        }
    )

    encoded = json.dumps(payload, indent=2, default=str)
    loaded = json.loads(encoded)

    assert loaded["exit_code"] == 3
    assert loaded["report_path"].endswith("outer.txt")
    assert loaded["nested"]["paths"][0].endswith("a.txt")


def test_scalar_results_are_wrapped_in_result_object() -> None:
    for value in (0, 1, "failed", None, True):
        assert package_runner._json_safe_result(value) == {"result": value}


def test_path_and_enum_top_level_results_are_wrapped(tmp_path: Path) -> None:
    path_payload = package_runner._json_safe_result(tmp_path / "report.txt")
    enum_payload = package_runner._json_safe_result(DemoKind.OK)

    assert path_payload["result"].endswith("report.txt")
    assert enum_payload == {"result": "ok"}


def test_to_dict_result_serializes(tmp_path: Path) -> None:
    class DictableResult:
        def to_dict(self) -> dict[str, object]:
            return {"exit_code": 9, "report_path": tmp_path / "dictable.txt"}

    payload = package_runner._json_safe_result(DictableResult())
    encoded = json.dumps(payload, indent=2, default=str)
    loaded = json.loads(encoded)

    assert loaded["exit_code"] == 9
    assert loaded["report_path"].endswith("dictable.txt")


def test_custom_object_falls_back_to_type_and_repr() -> None:
    class CustomResult:
        pass

    payload = package_runner._json_safe_result(CustomResult())

    assert payload["result_type"] == "CustomResult"
    assert "CustomResult" in payload["result_repr"]


def test_cli_main_source_uses_safe_result_serializer() -> None:
    source = Path(package_runner.__file__).read_text(encoding="utf-8")
    compact = re.sub(r"\s+", "", source)

    assert "_json_safe_result(result)" in source
    assert "json.dumps(asdict(result),indent=2)" not in compact
