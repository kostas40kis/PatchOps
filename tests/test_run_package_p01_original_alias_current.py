from __future__ import annotations

from patchops import package_runner


def test_p01_run_package_wrapper_captures_original_callable() -> None:
    original = getattr(package_runner, "_PATCHOPS_P01_V8_ORIGINAL_RUN_DELIVERY_PACKAGE", None)

    assert callable(original)
    assert original is not package_runner.run_delivery_package
