from pathlib import Path

from patchops.files.paths import normalize_path_string, safe_relative_path


def test_normalize_windows_path_string():
    assert normalize_path_string(r"C:/dev/trader") == r"C:\dev\trader"


def test_safe_relative_path_falls_back_to_filename():
    result = safe_relative_path(Path("/tmp/a.txt"), Path("/other"))
    assert result == Path("a.txt")
