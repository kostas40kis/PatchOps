from __future__ import annotations

import py_compile
import warnings
from pathlib import Path


def test_operator_scripts_compile_without_syntax_warnings() -> None:
    source = Path("patchops/operator_scripts.py")
    assert source.exists()

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        py_compile.compile(str(source), doraise=True)
