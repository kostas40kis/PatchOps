from __future__ import annotations

import ast
from pathlib import Path

import pytest

from patchops.llm_browser.live_adapter import (
    LiveAdapterPolicy,
    LiveAdapterStatus,
    create_live_adapter_skeleton,
)


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_live_adapter_skeleton_imports_without_selenium_dependency() -> None:
    text = _read("patchops/llm_browser/live_adapter.py")
    tree = ast.parse(text)

    imported_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.append(node.module)

    assert all("selenium" not in name.lower() for name in imported_names)


def test_live_adapter_default_capabilities_are_no_side_effect() -> None:
    adapter = create_live_adapter_skeleton()
    capabilities = adapter.describe_capabilities()

    assert capabilities["stream"] == "L1"
    assert capabilities["phase"] == "L1.1"
    assert capabilities["selenium_required"] is False
    assert capabilities["browser_starts"] is False
    assert capabilities["side_effects_supported"] is False
    assert capabilities["supported_operations"] == []
    assert "start_browser" in capabilities["blocked_operations"]
    assert "send_or_submit" in capabilities["blocked_operations"]


def test_live_adapter_policy_defaults_block_every_side_effect() -> None:
    policy = LiveAdapterPolicy()

    assert policy.enable_live_browser is False
    assert policy.allow_download_click is False
    assert policy.allow_patchops_execution is False
    assert policy.allow_composer_paste is False
    assert policy.allow_send_submit is False


@pytest.mark.parametrize(
    "method_name",
    [
        "start_browser",
        "read_page",
        "detect_latest_assistant_reply",
        "click_download",
        "run_patchops_package",
        "paste_to_composer",
    ],
)
def test_live_adapter_skeleton_blocks_side_effect_methods(method_name: str) -> None:
    adapter = create_live_adapter_skeleton()
    result = getattr(adapter, method_name)()

    assert result.ok is False
    assert result.status is LiveAdapterStatus.BLOCKED
    assert result.side_effects_performed == ()
    assert result.details["operation"] == method_name
    assert result.details["phase"] == "L1.1"
    assert result.to_dict()["side_effects_performed"] == []


def test_live_adapter_skeleton_send_submit_is_unsupported() -> None:
    adapter = create_live_adapter_skeleton()
    result = adapter.send_or_submit()

    assert result.ok is False
    assert result.status is LiveAdapterStatus.UNSUPPORTED
    assert result.side_effects_performed == ()
    assert result.details["operation"] == "send_or_submit"
    assert result.details["auto_send_supported"] is False
    assert "unsupported" in result.reason.lower()


def test_live_adapter_skeleton_still_blocks_with_permissive_policy() -> None:
    policy = LiveAdapterPolicy(
        enable_live_browser=True,
        allow_download_click=True,
        allow_patchops_execution=True,
        allow_composer_paste=True,
        allow_send_submit=True,
    )
    adapter = create_live_adapter_skeleton(policy=policy)

    assert adapter.describe_capabilities()["policy"]["enable_live_browser"] is True
    assert adapter.start_browser().ok is False
    assert adapter.click_download().ok is False
    assert adapter.run_patchops_package().ok is False
    assert adapter.paste_to_composer().ok is False
    assert adapter.send_or_submit().ok is False


def test_live_adapter_skeleton_docs_define_l1_1_contract() -> None:
    text = _read("docs/llm_browser_live_adapter_skeleton.md")

    required = [
        "LLM Browser L1.1 Live Adapter Skeleton Contract",
        "does not start a browser",
        "does not require Selenium",
        "no browser startup",
        "no download click",
        "no PatchOps package execution",
        "no composer paste",
        "no send/submit",
        "No import of Selenium is allowed",
        "L1.2 Live adapter skeleton CLI/readback",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_runner_doc_links_l1_1_skeleton() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "L1.1 live adapter skeleton contract",
        "patchops/llm_browser/live_adapter.py",
        "docs/llm_browser_live_adapter_skeleton.md",
        "tests/test_llm_browser_live_adapter_skeleton_current.py",
        "no Selenium import is allowed",
        "no browser starts",
        "no download click happens",
        "no composer paste happens",
        "no send/submit is supported",
        "L1.2 Live adapter skeleton CLI/readback",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
