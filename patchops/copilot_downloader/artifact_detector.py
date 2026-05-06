from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


ALLOWED_SUFFIXES = (".zip", ".ps1", ".txt", ".md")
DEFAULT_EXCLUDED_DIR_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "data/runtime",
    "data\\runtime",
}


@dataclass(frozen=True)
class DownloaderSafetyFlags:
    patchops_invoked: bool = False
    artifact_executed: bool = False
    browser_used: bool = False
    clipboard_written: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class ArtifactCandidate:
    path: str
    name: str
    suffix: str
    size_bytes: int
    sha256: str
    modified_time_epoch: float
    age_seconds: float
    classification: str
    stable: bool
    reason: str


@dataclass(frozen=True)
class DetectionResult:
    ok: bool
    status: str
    scan_roots: tuple[str, ...]
    candidate_count: int
    stable_candidate_count: int
    candidates: tuple[ArtifactCandidate, ...]
    selected: ArtifactCandidate | None
    safety_flags: DownloaderSafetyFlags
    output_paths: dict[str, str]
    reason: str

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        return payload


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def normalize_root(root: str | Path) -> Path:
    return Path(root).expanduser().resolve()


def is_excluded(path: Path, *, excluded_parts: Iterable[str] = DEFAULT_EXCLUDED_DIR_PARTS) -> bool:
    text = str(path)
    parts = {p.lower() for p in path.parts}
    for excluded in excluded_parts:
        ex = excluded.lower()
        if ex in parts or ex in text.lower():
            return True
    return False


def classify_artifact(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if suffix == ".zip":
        if "patchops_bundle" in name or "patchops" in name:
            return "patchops_zip_bundle"
        return "zip_candidate"
    if suffix == ".ps1":
        return "powershell_script"
    if suffix == ".txt":
        if "report" in name or "patchops" in name:
            return "patchops_text_report_or_handoff"
        return "text_candidate"
    if suffix == ".md":
        return "markdown_handoff_or_plan"
    return "unknown"


def iter_candidate_paths(
    roots: Sequence[str | Path],
    *,
    allowed_suffixes: Sequence[str] = ALLOWED_SUFFIXES,
    recursive: bool = False,
) -> tuple[Path, ...]:
    suffixes = {s.lower() for s in allowed_suffixes}
    found: list[Path] = []
    for root_value in roots:
        root = normalize_root(root_value)
        if not root.exists():
            continue
        if root.is_file():
            # Explicit file paths are operator-selected candidates, even when
            # they live under data/runtime. Directory scans still exclude
            # runtime/cache folders to avoid accidental self-detection noise.
            if root.suffix.lower() in suffixes:
                found.append(root)
            continue

        iterator = root.rglob("*") if recursive else root.glob("*")
        for path in iterator:
            if path.is_file() and path.suffix.lower() in suffixes and not is_excluded(path):
                found.append(path.resolve())

    return tuple(sorted(set(found), key=lambda p: (p.stat().st_mtime, str(p)), reverse=True))


def build_candidate(path: Path, *, now_epoch: float | None = None, min_stable_age_seconds: float = 2.0) -> ArtifactCandidate:
    now = time.time() if now_epoch is None else now_epoch
    stat = path.stat()
    age = max(0.0, now - stat.st_mtime)
    stable = age >= min_stable_age_seconds and stat.st_size > 0
    if stat.st_size <= 0:
        reason = "empty file is not a runnable/downloadable artifact"
    elif not stable:
        reason = f"candidate is too new to be considered stable; age_seconds={age:.3f}"
    else:
        reason = "candidate is stable by age and non-empty size"

    return ArtifactCandidate(
        path=str(path),
        name=path.name,
        suffix=path.suffix.lower(),
        size_bytes=stat.st_size,
        sha256=sha256_file(path),
        modified_time_epoch=stat.st_mtime,
        age_seconds=age,
        classification=classify_artifact(path),
        stable=stable,
        reason=reason,
    )


def detect_artifacts(
    roots: Sequence[str | Path],
    *,
    recursive: bool = False,
    min_stable_age_seconds: float = 2.0,
    now_epoch: float | None = None,
) -> DetectionResult:
    normalized_roots = tuple(str(normalize_root(r)) for r in roots)
    paths = iter_candidate_paths(roots, recursive=recursive)
    candidates = tuple(
        build_candidate(path, now_epoch=now_epoch, min_stable_age_seconds=min_stable_age_seconds)
        for path in paths
    )
    stable = tuple(c for c in candidates if c.stable)
    selected = stable[0] if stable else None
    if selected is not None:
        status = "PASS_ARTIFACT_DETECTED"
        ok = True
        reason = "Stable artifact candidate detected. PatchOps execution is intentionally deferred."
    elif candidates:
        status = "BLOCKED_NO_STABLE_ARTIFACT"
        ok = False
        reason = "Candidates were found, but none were stable/non-empty yet."
    else:
        status = "BLOCKED_NO_ARTIFACTS"
        ok = False
        reason = "No candidate artifacts were found in the scan roots."

    return DetectionResult(
        ok=ok,
        status=status,
        scan_roots=normalized_roots,
        candidate_count=len(candidates),
        stable_candidate_count=len(stable),
        candidates=candidates,
        selected=selected,
        safety_flags=DownloaderSafetyFlags(),
        output_paths={},
        reason=reason,
    )


def write_detection_result(result: DetectionResult, output_dir: str | Path) -> DetectionResult:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "artifact_detection_result.json"
    txt_path = out / "artifact_detection_result.txt"

    payload = result.to_payload()
    payload["output_paths"] = {"json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "PATCHOPS_COPILOT_DOWNLOADER_ARTIFACT_DETECTION",
        f"Status              : {result.status}",
        f"Ok                  : {str(result.ok).lower()}",
        f"CandidateCount      : {result.candidate_count}",
        f"StableCandidateCount: {result.stable_candidate_count}",
        f"Reason              : {result.reason}",
        "SCAN_ROOTS",
    ]
    for root in result.scan_roots:
        lines.append(f"- {root}")
    if result.selected is not None:
        lines.extend(
            [
                "SELECTED",
                f"  path          : {result.selected.path}",
                f"  name          : {result.selected.name}",
                f"  classification: {result.selected.classification}",
                f"  size_bytes    : {result.selected.size_bytes}",
                f"  sha256        : {result.selected.sha256}",
            ]
        )
    lines.append("CANDIDATES")
    if not result.candidates:
        lines.append("<none>")
    for index, candidate in enumerate(result.candidates, 1):
        lines.append(
            f"[{index}] stable={str(candidate.stable).lower()} "
            f"classification={candidate.classification} size={candidate.size_bytes} "
            f"age={candidate.age_seconds:.3f} path={candidate.path}"
        )
    lines.append("SAFETY_FLAGS")
    for key, value in asdict(result.safety_flags).items():
        lines.append(f"{key}:{str(value).lower()}")
    lines.append("END_PATCHOPS_COPILOT_DOWNLOADER_ARTIFACT_DETECTION")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return DetectionResult(
        ok=result.ok,
        status=result.status,
        scan_roots=result.scan_roots,
        candidate_count=result.candidate_count,
        stable_candidate_count=result.stable_candidate_count,
        candidates=result.candidates,
        selected=result.selected,
        safety_flags=result.safety_flags,
        output_paths={"json_path": str(json_path), "txt_path": str(txt_path)},
        reason=result.reason,
    )


def create_sample_artifact(output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    sample = out / "sample_patchops_bundle.zip"
    sample.write_bytes(b"sample patchops bundle bytes for D0.1 downloader detection\n")
    old_time = time.time() - 10
    try:
        import os
        os.utime(sample, (old_time, old_time))
    except Exception:
        pass
    return sample


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="D0.1 PatchOps Co-Pilot downloader artifact detector")
    parser.add_argument("--scan-root", action="append", default=None, help="Directory or file to scan. Can be repeated.")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--min-stable-age-seconds", type=float, default=2.0)
    parser.add_argument("--sample-artifact", action="store_true")
    parser.add_argument("--output-dir", default="data/runtime/d0_01_copilot_downloader_artifact_detector")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    roots = args.scan_root or []
    if args.sample_artifact:
        sample = create_sample_artifact(args.output_dir)
        roots.append(str(sample))
    if not roots:
        raise SystemExit("Provide --scan-root or --sample-artifact")

    result = detect_artifacts(
        roots,
        recursive=args.recursive,
        min_stable_age_seconds=args.min_stable_age_seconds,
    )
    result = write_detection_result(result, args.output_dir)

    if args.json:
        print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    else:
        print(result.status)
        print(result.reason)
        for key, path in result.output_paths.items():
            print(f"{key}: {path}")

    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
