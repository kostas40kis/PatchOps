from pathlib import Path


def test_examples_doc_preserves_example_contract_and_handoff_note() -> None:
    text = Path("docs/examples.md").read_text(encoding="utf-8")
    lowered = text.lower()

    required_fragments = [
        "trader code patch example",
        "trader verification-only example",
        "generic python example",
        "documentation-only example",
        "examples/trader_code_patch.json",
        "examples/trader_first_verify_patch.json",
        "examples/generic_python_patch.json",
        "examples/trader_first_doc_patch.json",
        "powershell/invoke-patchverify.ps1",
    ]
    for fragment in required_fragments:
        assert fragment.lower() in lowered

    assert "Start from examples and adapt them." in text
    assert "If you are uncertain, start narrower." in text
    assert "That is the intended starting surface for practical PatchOps usage." in text
    assert "Examples are no longer the first state-reconstruction surface" in text


def test_handoff_surface_doc_marks_patch_69_stop() -> None:
    text = Path("docs/handoff_surface.md").read_text(encoding="utf-8")

    assert "Patch 69 is the documentation stop for the handoff-first UX." in text
    assert "`README.md`" in text
    assert "`docs/project_status.md`" in text
    assert "`docs/examples.md`" in text
    assert "`docs/llm_usage.md`" in text
    assert "Future onboarding should now start from the handoff artifact" in text
