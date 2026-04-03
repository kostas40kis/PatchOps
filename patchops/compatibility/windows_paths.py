from pathlib import Path


def is_windows_style_path(value: str) -> bool:
    return len(value) >= 2 and value[1] == ":"


def normalize_windowsish_path(value: str) -> Path:
    return Path(value)
