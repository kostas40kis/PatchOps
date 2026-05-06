from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.assisted_upload_helper import (
    build_instructions,
    has_secret_like_content,
    prepare_assisted_upload_packet,
    safe_upload_filename,
)


def test_assisted_upload_packet_stages_safe_file_without_uploading(tmp_path: Path) -> None:
    src = tmp_path / "report.txt"
    src.write_text("Result : PASS\nExitCode : 0\nsafe report\n", encoding="utf-8")

    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet")

    assert packet.ok is True
    assert packet.status == "PASS_ASSISTED_UPLOAD_PACKET_READY"
    assert packet.staged_count == 1
    assert packet.candidates[0].ok is True
    assert packet.candidates[0].staged_path is not None
    assert Path(packet.candidates[0].staged_path).exists()
    assert packet.safety_flags.upload_packet_prepared is True
    assert packet.safety_flags.file_upload_attempted is False
    assert packet.safety_flags.chatgpt_submit_performed is False
    assert packet.safety_flags.selenium_used is False
    assert Path(packet.manifest_path).exists()
    assert Path(packet.instructions_path).exists()


def test_missing_file_blocks_without_staging(tmp_path: Path) -> None:
    packet = prepare_assisted_upload_packet(input_paths=[tmp_path / "missing.txt"], output_dir=tmp_path / "packet")

    assert packet.ok is False
    assert packet.status == "BLOCKED_NO_FILES_STAGED"
    assert packet.staged_count == 0
    assert packet.candidates[0].status == "BLOCKED_SOURCE_NOT_FOUND"


def test_empty_file_blocks_without_staging(tmp_path: Path) -> None:
    src = tmp_path / "empty.txt"
    src.write_text("", encoding="utf-8")

    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet")

    assert packet.ok is False
    assert packet.candidates[0].status == "BLOCKED_EMPTY_FILE"


def test_file_too_large_blocks_without_staging(tmp_path: Path) -> None:
    src = tmp_path / "large.txt"
    src.write_text("x" * 120, encoding="utf-8")

    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet", max_file_bytes=100)

    assert packet.ok is False
    assert packet.candidates[0].status == "BLOCKED_FILE_TOO_LARGE"


def test_secret_like_content_blocks_by_default(tmp_path: Path) -> None:
    src = tmp_path / "secret.txt"
    src.write_text("api_key = '" + ("A" * 32) + "'\n", encoding="utf-8")

    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet")

    assert packet.ok is False
    assert packet.candidates[0].status == "BLOCKED_SECRET_LIKE_CONTENT"
    assert has_secret_like_content(src) is True


def test_secret_like_content_can_be_allowed_explicitly(tmp_path: Path) -> None:
    src = tmp_path / "secret.txt"
    src.write_text("api_key = '" + ("A" * 32) + "'\n", encoding="utf-8")

    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet", allow_secret_risk=True)

    assert packet.ok is True
    assert packet.candidates[0].status == "PASS_FILE_STAGED_FOR_MANUAL_UPLOAD"


def test_partial_packet_when_one_input_blocks(tmp_path: Path) -> None:
    safe = tmp_path / "safe.txt"
    safe.write_text("safe\n", encoding="utf-8")

    packet = prepare_assisted_upload_packet(
        input_paths=[safe, tmp_path / "missing.txt"],
        output_dir=tmp_path / "packet",
    )

    assert packet.ok is True
    assert packet.status == "PASS_PARTIAL_ASSISTED_UPLOAD_PACKET_READY"
    assert packet.staged_count == 1
    assert packet.candidate_count == 2


def test_safe_upload_filename_sanitizes_names(tmp_path: Path) -> None:
    name = safe_upload_filename(tmp_path / "bad name @#$%.txt", index=7)
    assert name.startswith("007_")
    assert name.endswith(".txt")
    assert " " not in name
    assert "@" not in name


def test_instructions_keep_manual_only_boundary(tmp_path: Path) -> None:
    src = tmp_path / "report.txt"
    src.write_text("safe\n", encoding="utf-8")
    packet = prepare_assisted_upload_packet(input_paths=[src], output_dir=tmp_path / "packet")

    instructions = build_instructions(packet)

    assert "does not open a browser" in instructions
    assert "does not click upload controls" in instructions
    assert "does not send" in instructions
    assert "file_upload_attempted:false" in instructions
    assert "chatgpt_submit_performed:false" in instructions
