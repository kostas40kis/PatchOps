from __future__ import annotations

import ast
import sys
from pathlib import Path


IMPORT_LINE = "from patchops.failure_categories import normalize_failure_category"
HELPER_BLOCK = '''

def _normalize_failure_info(failure):
    if failure is None:
        return None
    category = getattr(failure, "category", None)
    normalized_category = normalize_failure_category(category)
    if normalized_category == category:
        return failure
    details = getattr(failure, "details", None)
    message = getattr(failure, "message", "")
    return type(failure)(
        category=normalized_category,
        message=message,
        details=details,
    )
'''

TEST_CONTENT = '''from __future__ import annotations

from types import SimpleNamespace

import pytest


def test_apply_workflow_normalize_helper_delegates_to_normalizer(monkeypatch: pytest.MonkeyPatch) -> None:
    from patchops.workflows import apply_patch as module

    seen: dict[str, object] = {}

    def fake_normalize(category: object) -> object:
        seen["category"] = category
        return "wrapper_failure"

    monkeypatch.setattr(module, "normalize_failure_category", fake_normalize)
    failure = SimpleNamespace(category="wrapper mechanics failure", message="boom", details={"x": 1})

    normalized = module._normalize_failure_info(failure)

    assert seen["category"] == "wrapper mechanics failure"
    assert normalized.category == "wrapper_failure"
    assert normalized.message == "boom"
    assert normalized.details == {"x": 1}


def test_apply_workflow_normalize_helper_passes_through_when_category_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    from patchops.workflows import apply_patch as module

    monkeypatch.setattr(module, "normalize_failure_category", lambda category: category)
    failure = SimpleNamespace(category=None, message="boom", details=None)

    normalized = module._normalize_failure_info(failure)

    assert normalized is failure
'''


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("usage: repair_mp33a.py <backup_apply_path> <target_apply_path> <target_test_path>")

    backup_apply_path = Path(sys.argv[1])
    target_apply_path = Path(sys.argv[2])
    target_test_path = Path(sys.argv[3])

    source = backup_apply_path.read_text(encoding="utf-8")
    module = ast.parse(source)
    body = list(module.body)

    start_index = 0
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) and isinstance(body[0].value.value, str):
        start_index = 1

    import_end_lineno = None
    for node in body[start_index:]:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_end_lineno = getattr(node, "end_lineno", None) or node.lineno
            continue
        break

    if import_end_lineno is None:
        raise RuntimeError("Could not locate top-level import block in backup apply_patch.py")

    lines = source.splitlines()
    if IMPORT_LINE not in source:
        lines.insert(import_end_lineno, IMPORT_LINE)

    rebuilt = "\n".join(lines) + "\n"

    if "def _normalize_failure_info(" not in rebuilt:
        module2 = ast.parse(rebuilt)
        insertion_lineno = None
        for node in module2.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                insertion_lineno = node.lineno
                break
        if insertion_lineno is None:
            raise RuntimeError("Could not locate top-level function/class insertion point in apply_patch.py")
        lines2 = rebuilt.splitlines()
        lines2.insert(insertion_lineno - 1, HELPER_BLOCK.rstrip("\n"))
        rebuilt = "\n".join(lines2) + "\n"

    if "failure=_normalize_failure_info(failure)," not in rebuilt:
        marker = "failure=failure,"
        if marker not in rebuilt:
            raise RuntimeError("Could not locate failure assignment marker in apply_patch.py")
        rebuilt = rebuilt.replace(marker, "failure=_normalize_failure_info(failure),", 1)

    ast.parse(rebuilt)

    target_apply_path.parent.mkdir(parents=True, exist_ok=True)
    target_apply_path.write_text(rebuilt, encoding="utf-8")

    target_test_path.parent.mkdir(parents=True, exist_ok=True)
    target_test_path.write_text(TEST_CONTENT, encoding="utf-8")

    print(str(backup_apply_path))
    print(str(target_apply_path))
    print(str(target_test_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())