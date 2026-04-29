# Optional dependency doctor for the PatchOps LLM browser runner.
#
# This module is intentionally passive:
# - it imports no Selenium modules,
# - it starts no browser driver,
# - it opens no browser window,
# - it creates no network listener.

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import platform
import sys
from typing import Callable, Mapping

from .browser_paths import (
    edge_candidate_paths,
    find_browser_path,
    first_existing_path,
    opera_candidate_paths,
)


ImportProbe = Callable[[str], bool]


OPTIONAL_IMPORTS: tuple[tuple[str, str], ...] = (
    ("selenium", "selenium"),
    ("webdriver-manager", "webdriver_manager"),
    ("psutil", "psutil"),
    ("pyperclip", "pyperclip"),
)


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    ok: bool
    detail: str
    required: bool = True

    @property
    def status(self) -> str:
        if self.ok:
            return "OK"
        return "FAIL" if self.required else "WARN"

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "ok": self.ok,
            "status": self.status,
            "detail": self.detail,
            "required": self.required,
        }


@dataclass(frozen=True)
class BrowserDoctorReport:
    checks: tuple[DoctorCheck, ...]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks if check.required)

    @property
    def result(self) -> str:
        return "PASS" if self.ok else "FAIL"

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    def to_payload(self) -> dict[str, object]:
        return {
            "result": self.result,
            "ok": self.ok,
            "checks": [check.to_payload() for check in self.checks],
        }

    def render_lines(self) -> list[str]:
        rows = ["Browser Runner Doctor"]
        for check in self.checks:
            rows.append(f"{check.name:<20}: {check.status} - {check.detail}")
        rows.append(f"Result              : {self.result}")
        return rows


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _path_exists(path: Path) -> bool:
    return path.exists()


def _normalize_required_browser(value: str | None) -> str:
    normalized = (value or "edge").strip().lower()
    if normalized not in {"edge", "opera", "both", "none"}:
        raise ValueError("browser must be one of: edge, opera, both, none")
    return normalized


def build_dependency_report(
    *,
    wrapper_root: str | Path | None = None,
    target_root: str | Path | None = None,
    download_dir: str | Path | None = None,
    browser: str = "edge",
    import_probe: ImportProbe | None = None,
    exists: Callable[[Path], bool] = _path_exists,
    environ: Mapping[str, str] | None = None,
) -> BrowserDoctorReport:
    if import_probe is None:
        import_probe = _module_available

    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            "Python",
            sys.version_info >= (3, 11),
            f"{platform.python_implementation()} {platform.python_version()}",
            required=True,
        )
    )

    for display_name, module_name in OPTIONAL_IMPORTS:
        available = import_probe(module_name)
        checks.append(
            DoctorCheck(
                display_name,
                available,
                "import available" if available else f"missing import: {module_name}",
                required=True,
            )
        )

    selected_browser = _normalize_required_browser(browser)

    edge_result = find_browser_path("edge", environ=environ, exists=exists)
    checks.append(
        DoctorCheck(
            "Edge installed",
            edge_result.found,
            str(edge_result.executable_path) if edge_result.executable_path else edge_result.message,
            required=selected_browser in {"edge", "both"},
        )
    )

    opera_result = find_browser_path("opera", environ=environ, exists=exists)
    checks.append(
        DoctorCheck(
            "Opera installed",
            opera_result.found,
            str(opera_result.executable_path) if opera_result.executable_path else opera_result.message,
            required=selected_browser in {"opera", "both"},
        )
    )

    resolved_download_dir = Path(download_dir).expanduser() if download_dir else Path.home() / "Downloads"
    checks.append(DoctorCheck("Downloads", exists(resolved_download_dir), str(resolved_download_dir), required=True))

    resolved_wrapper_root = Path(wrapper_root).expanduser() if wrapper_root else Path.cwd()
    checks.append(DoctorCheck("Wrapper root", exists(resolved_wrapper_root), str(resolved_wrapper_root), required=True))

    if target_root is not None:
        resolved_target_root = Path(target_root).expanduser()
        checks.append(DoctorCheck("Target root", exists(resolved_target_root), str(resolved_target_root), required=True))

    return BrowserDoctorReport(tuple(checks))


def render_dependency_report(report: BrowserDoctorReport) -> str:
    return "\n".join(report.render_lines()) + "\n"
