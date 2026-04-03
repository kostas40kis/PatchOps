from pathlib import Path


def test_readme_mentions_suspicious_run_support():
    text = Path("README.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "suspicious-run" in lowered
    assert "wrapper health aid" in lowered
    assert "opt-in" in lowered or "opt in" in lowered


def test_project_status_mentions_pythonization_stream_note():
    text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()
    assert "pythonization micro-patch stream" in text
    assert "suspicious-run rule detection" in text
    assert "optional artifact emission" in text


def test_operator_quickstart_mentions_how_to_read_suspicious_runs():
    text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    assert "suspicious-run" in text
    assert "canonical report" in text
    assert "artifact emission" in text or "artifact" in text


def test_wrapper_self_hosted_packet_mentions_suspicious_run_support_when_present():
    packet = Path("docs/projects/wrapper_self_hosted.md")
    if not packet.exists():
        return
    text = packet.read_text(encoding="utf-8").lower()
    assert "suspicious-run" in text
    assert "optional artifact emission" in text or "artifact emission" in text
