from pathlib import Path


def test_readme_points_to_handoff_first_takeover_and_preserves_profile_example_mentions() -> None:
    text = Path("README.md").read_text(encoding="utf-8")

    assert "Read these files in this order:" in text
    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text
    assert "run handoff export" in text
    assert "paste `handoff/next_prompt.txt`" in text
    assert "Generic Python + PowerShell profile examples" in text
    assert "generic_python_powershell" in text


def test_project_status_keeps_old_snapshot_language_and_new_handoff_first_language() -> None:
    text = Path("docs/project_status.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "current state snapshot" in lowered
    assert "stable now" in lowered
    assert "exists in the repo today" in lowered
    assert "future work, not yet shipped behavior" in lowered
    assert "what remains future work rather than current behavior" in lowered
    assert "patch 41" in lowered
    assert "patch 48" in lowered
    assert "verification-only reruns" in text
    assert "wrapper-only retry classification support" in text
    assert "powershell/Invoke-PatchVerify.ps1" in text
    assert "patchops.cli examples" in text
    assert "completed through Patch 69" in text
    assert "run one export command" in text
    assert "paste one generated prompt" in text


def test_examples_doc_preserves_older_example_contract_and_handoff_note() -> None:
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


def test_llm_usage_doc_preserves_wrapper_boundary_and_handoff_first_read_order() -> None:
    text = Path("docs/llm_usage.md").read_text(encoding="utf-8")
    lowered = text.lower()

    assert "PatchOps is a **standalone wrapper / harness project**." in text
    assert "Target repos own:" in text
    assert "Never move target-repo business logic into PatchOps" in text
    assert "Trader is the first serious profile, not the identity of the wrapper." in text

    required_fragments = [
        "how to read the project",
        "how to pick a profile",
        "how to build a manifest",
        "how to decide between apply and verify-only",
        "how to classify failure",
        "how to avoid moving target-repo logic into patchops",
        "docs/failure_repair_guide.md",
        "examples/trader_first_verify_patch.json",
        "powershell/invoke-patchverify.ps1",
    ]
    for fragment in required_fragments:
        assert fragment in lowered

    assert "1. `handoff/current_handoff.md`" in text
    assert "2. `handoff/current_handoff.json`" in text
    assert "3. `handoff/latest_report_copy.txt`" in text