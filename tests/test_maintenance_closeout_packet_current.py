from pathlib import Path


def test_maintenance_freeze_packet_contains_closeout_contract() -> None:
    text = Path("docs/maintenance_freeze_packet.md").read_text(encoding="utf-8")

    required_phrases = [
        "final maintenance closeout packet",
        "maintenance / additive improvement",
        "Do **not** redesign PatchOps.",
        "Keep PowerShell thin.",
        "Keep reusable mechanics in Python.",
        "one canonical Desktop txt report",
        "Patch 21",
        "Patch 22",
        "Patch 23",
        "Patch 24",
        "doc contract tests",
        "command/doc alignment proof",
        "maintainer packet completeness check",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_bundle_contract_packet_contains_canonical_bundle_shape_and_guardrails() -> None:
    text = Path("docs/bundle_contract_packet.md").read_text(encoding="utf-8")

    required_phrases = [
        "manifest.json",
        "bundle_meta.json",
        "README.txt",
        "run_with_patchops.ps1",
        "content/",
        "bundle-entry",
        "Keep PowerShell thin.",
        "Keep reusable mechanics in Python.",
        "Keep one canonical Desktop txt report.",
        "Command/doc alignment proof",
    ]
    for phrase in required_phrases:
        assert phrase in text
