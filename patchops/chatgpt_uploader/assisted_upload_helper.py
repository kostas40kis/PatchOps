from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_MAX_FILE_BYTES = 4 * 1024 * 1024

_SECRET_PATTERNS = (
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)secret\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)token\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


@dataclass(frozen=True)
class AssistedUploadSafetyFlags:
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False
    clipboard_written: bool = False
    paste_attempted: bool = False
    upload_packet_prepared: bool = False
    source_content_logged: bool = False


@dataclass(frozen=True)
class AssistedUploadCandidate:
    source_path: str
    staged_path: str | None
    file_name: str
    size_bytes: int
    sha256: str | None
    ok: bool
    status: str
    reason: str


@dataclass(frozen=True)
class AssistedUploadPacket:
    ok: bool
    status: str
    reason: str
    packet_dir: str
    manifest_path: str
    instructions_path: str
    candidate_count: int
    staged_count: int
    max_file_bytes: int
    candidates: tuple[AssistedUploadCandidate, ...]
    safety_flags: AssistedUploadSafetyFlags

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        return payload


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def has_secret_like_content(path: Path, *, max_scan_bytes: int = 256_000) -> bool:
    try:
        data = path.read_bytes()[:max_scan_bytes]
    except OSError:
        return False
    text = data.decode("utf-8", errors="ignore")
    return any(pattern.search(text) for pattern in _SECRET_PATTERNS)


def safe_upload_filename(path: Path, *, index: int) -> str:
    suffix = path.suffix if path.suffix else ".txt"
    stem = path.stem or "upload"
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")
    if not cleaned:
        cleaned = "upload"
    return f"{index:03d}_{cleaned}{suffix}"


def prepare_assisted_upload_packet(
    *,
    input_paths: Iterable[str | Path],
    output_dir: str | Path,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    allow_secret_risk: bool = False,
) -> AssistedUploadPacket:
    packet_dir = Path(output_dir)
    packet_dir.mkdir(parents=True, exist_ok=True)
    files_dir = packet_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    candidates: list[AssistedUploadCandidate] = []
    staged_count = 0

    for index, raw in enumerate(input_paths, 1):
        source = Path(raw)
        file_name = source.name or f"input_{index}.txt"

        if not source.exists() or not source.is_file():
            candidates.append(
                AssistedUploadCandidate(
                    source_path=str(source),
                    staged_path=None,
                    file_name=file_name,
                    size_bytes=0,
                    sha256=None,
                    ok=False,
                    status="BLOCKED_SOURCE_NOT_FOUND",
                    reason="Source path does not exist or is not a file.",
                )
            )
            continue

        size = source.stat().st_size
        digest = sha256_file(source)

        if size == 0:
            candidates.append(
                AssistedUploadCandidate(
                    source_path=str(source),
                    staged_path=None,
                    file_name=file_name,
                    size_bytes=size,
                    sha256=digest,
                    ok=False,
                    status="BLOCKED_EMPTY_FILE",
                    reason="Source file is empty.",
                )
            )
            continue

        if size > max_file_bytes:
            candidates.append(
                AssistedUploadCandidate(
                    source_path=str(source),
                    staged_path=None,
                    file_name=file_name,
                    size_bytes=size,
                    sha256=digest,
                    ok=False,
                    status="BLOCKED_FILE_TOO_LARGE",
                    reason=f"Source file exceeds max_file_bytes={max_file_bytes}.",
                )
            )
            continue

        if has_secret_like_content(source) and not allow_secret_risk:
            candidates.append(
                AssistedUploadCandidate(
                    source_path=str(source),
                    staged_path=None,
                    file_name=file_name,
                    size_bytes=size,
                    sha256=digest,
                    ok=False,
                    status="BLOCKED_SECRET_LIKE_CONTENT",
                    reason="Secret-like content detected; refusing to stage for assisted upload.",
                )
            )
            continue

        staged_name = safe_upload_filename(source, index=index)
        staged = files_dir / staged_name
        shutil.copyfile(source, staged)
        staged_digest = sha256_file(staged)
        if staged_digest != digest:
            candidates.append(
                AssistedUploadCandidate(
                    source_path=str(source),
                    staged_path=str(staged),
                    file_name=staged_name,
                    size_bytes=size,
                    sha256=digest,
                    ok=False,
                    status="BLOCKED_COPY_HASH_MISMATCH",
                    reason="Staged file hash does not match source file hash.",
                )
            )
            continue

        staged_count += 1
        candidates.append(
            AssistedUploadCandidate(
                source_path=str(source),
                staged_path=str(staged),
                file_name=staged_name,
                size_bytes=size,
                sha256=digest,
                ok=True,
                status="PASS_FILE_STAGED_FOR_MANUAL_UPLOAD",
                reason="File staged for manual assisted upload. No upload was attempted.",
            )
        )

    ok = staged_count > 0 and all(c.ok for c in candidates)
    if staged_count == 0:
        status = "BLOCKED_NO_FILES_STAGED"
        reason = "No files were staged for assisted upload."
    elif ok:
        status = "PASS_ASSISTED_UPLOAD_PACKET_READY"
        reason = "Assisted upload packet is ready for operator/manual upload."
    else:
        status = "PASS_PARTIAL_ASSISTED_UPLOAD_PACKET_READY"
        reason = "Some files were staged, but at least one input was blocked."

    manifest_path = packet_dir / "assisted_upload_manifest.json"
    instructions_path = packet_dir / "ASSISTED_UPLOAD_INSTRUCTIONS.txt"

    packet = AssistedUploadPacket(
        ok=staged_count > 0,
        status=status,
        reason=reason,
        packet_dir=str(packet_dir),
        manifest_path=str(manifest_path),
        instructions_path=str(instructions_path),
        candidate_count=len(candidates),
        staged_count=staged_count,
        max_file_bytes=max_file_bytes,
        candidates=tuple(candidates),
        safety_flags=AssistedUploadSafetyFlags(upload_packet_prepared=staged_count > 0),
    )

    manifest_path.write_text(json.dumps(packet.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    instructions_path.write_text(build_instructions(packet), encoding="utf-8")

    return packet


def build_instructions(packet: AssistedUploadPacket) -> str:
    lines = [
        "PATCHOPS ASSISTED FILE-UPLOAD PACKET",
        "====================================",
        f"Status     : {packet.status}",
        f"Reason     : {packet.reason}",
        f"PacketDir  : {packet.packet_dir}",
        f"StagedCount: {packet.staged_count}",
        "",
        "Operator steps:",
        "1. Review the staged file list below.",
        "2. If you choose to upload, use ChatGPT's normal UI manually.",
        "3. Do not send automatically; only send after explicit operator decision.",
        "",
        "Safety boundary:",
        "- this helper does not open a browser",
        "- this helper does not click upload controls",
        "- this helper does not paste",
        "- this helper does not send",
        "- this helper does not use Selenium/WebDriver",
        "- this helper does not bypass CAPTCHA/Cloudflare",
        "",
        "Files:",
    ]
    if not packet.candidates:
        lines.append("<none>")
    for candidate in packet.candidates:
        lines.extend([
            f"- status: {candidate.status}",
            f"  source_path: {candidate.source_path}",
            f"  staged_path: {candidate.staged_path}",
            f"  file_name: {candidate.file_name}",
            f"  size_bytes: {candidate.size_bytes}",
            f"  sha256: {candidate.sha256}",
            f"  reason: {candidate.reason}",
        ])
    lines.append("")
    lines.append("SAFETY_FLAGS")
    for key, value in asdict(packet.safety_flags).items():
        lines.append(f"{key}:{str(value).lower()}")
    lines.append("END_PATCHOPS_ASSISTED_FILE_UPLOAD_PACKET")
    return "\n".join(lines) + "\n"


def write_sample_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PATCHOPS SAMPLE ASSISTED UPLOAD FILE\n"
        "Result : PASS\n"
        "ExitCode : 0\n"
        "This file is safe sample text for a manual assisted upload packet.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U1.2 assisted file-upload helper")
    parser.add_argument("--input", action="append", default=[], help="Input file to stage. Can be repeated.")
    parser.add_argument("--sample-file", action="store_true", help="Create and stage a safe sample file.")
    parser.add_argument("--output-dir", default="data/runtime/u1_02_chatgpt_uploader_assisted_file_upload_helper")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--allow-secret-risk", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    inputs = [Path(p) for p in args.input]
    if args.sample_file:
        sample = out / "sample_assisted_upload_input.txt"
        write_sample_file(sample)
        inputs.append(sample)

    if not inputs:
        raise SystemExit("Provide --input at least once, or use --sample-file")

    packet = prepare_assisted_upload_packet(
        input_paths=inputs,
        output_dir=out / "assisted_upload_packet",
        max_file_bytes=args.max_file_bytes,
        allow_secret_risk=args.allow_secret_risk,
    )

    if args.json:
        print(json.dumps(packet.to_payload(), indent=2, sort_keys=True))
    else:
        print(packet.status)
        print(packet.reason)
        print(packet.manifest_path)
        print(packet.instructions_path)

    return 0 if packet.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
