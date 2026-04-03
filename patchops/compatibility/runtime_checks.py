from pathlib import Path


def runtime_exists(path: Path | None) -> bool:
    return bool(path and path.exists())
