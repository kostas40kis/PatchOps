from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").lower()


def test_readme_closes_patch_29_and_frontier_discrepancy() -> None:
    text = _read("README.md")

    assert "historical zip-first and python-heavier completion as architecture context" in text
    assert "patch 29 was unresolved and required the later recovery stream" in text
    assert "durable future-llm upload artifact" in text
    assert "current modular-package snapshot" in text


def test_project_status_distinguishes_history_from_live_frontier() -> None:
    text = _read("docs/project_status.md")

    assert "historical zip-first/python-heavier completion is real background context" in text
    assert "accepted live frontier is the later recovery and hardening frontier" in text
    assert "patch 29 was unresolved and required the recovery stream" in text
    assert "current modular package wording" in text


def test_llm_usage_treats_old_completion_language_as_context_only() -> None:
    text = _read("docs/llm_usage.md")

    assert "historical stream-completion summaries as context, not current frontier proof" in text
    assert "patch 29 as unresolved historical context that required the recovery stream" in text
    assert "handoff/final_future_llm_source_bundle.txt" in text
    assert "current modular package layout" in text


def test_operator_quickstart_uses_current_starter_surface_names() -> None:
    text = _read("docs/operator_quickstart.md")

    assert "patch 29 was unresolved and required the recovery stream" in text
    assert "historical zip-first/python-heavier completion is architecture context" in text
    assert "emit-operator-script" in text
    assert "setup-windows-env --dry-run" in text


def test_examples_page_rejects_stale_starter_surface_names() -> None:
    text = _read("docs/examples.md")

    assert "do not fall back to stale example or starter-surface names" in text
    assert "emit-operator-script" in text
    assert "setup-windows-env" in text
    assert "historical zip-first/python-heavier stream summaries as background context" in text
