from __future__ import annotations

import unittest
from pathlib import Path

from trader.execution.post_275_repo_inventory_refresh import (
    CURRENT_ACCEPTED_FRONTIER_PATCH,
    CURRENT_ACCEPTED_TEST_COUNT,
    IMPLEMENTATION_CENTER_OF_GRAVITY,
    OPERATOR_SUPPORT_SCRIPTS,
    build_post_275_inventory_summary,
    pilot_control_module_names,
    pilot_control_reference_paths,
    render_post_275_repo_inventory_section,
    validate_repo_inventory_text,
)


class Post275RepoInventoryRefreshTests(unittest.TestCase):
    def test_summary_recognizes_patch_275_as_current_frontier(self) -> None:
        summary = build_post_275_inventory_summary()
        self.assertEqual(CURRENT_ACCEPTED_FRONTIER_PATCH, 275)
        self.assertEqual(summary.current_frontier_patch, 275)
        self.assertEqual(summary.current_frontier_module, "cautious_live_widening_pilot_final_handoff_packet.py")
        self.assertEqual(CURRENT_ACCEPTED_TEST_COUNT, 1774)

    def test_operator_support_scripts_are_explicit(self) -> None:
        self.assertIn("scripts\\test_and_upload_trader_to_github.ps1", OPERATOR_SUPPORT_SCRIPTS)
        self.assertIn("scripts\\create_trader_green_checkpoint_tag.ps1", OPERATOR_SUPPORT_SCRIPTS)

    def test_pilot_control_family_is_represented(self) -> None:
        modules = pilot_control_module_names()
        self.assertIn("cautious_live_widening_pilot_runbook", modules)
        self.assertIn("cautious_live_widening_pilot_suite_runner", modules)
        self.assertIn("cautious_live_widening_pilot_final_handoff_packet", modules)
        self.assertGreaterEqual(len(modules), 20)

    def test_reference_paths_keep_canonical_layout(self) -> None:
        refs = pilot_control_reference_paths("cautious_live_widening_pilot_final_handoff_packet")
        paths = {ref.path for ref in refs}
        self.assertIn("src\\trader\\execution\\cautious_live_widening_pilot_final_handoff_packet.py", paths)
        self.assertIn("docs\\architecture\\cautious_live_widening_pilot_final_handoff_packet.md", paths)
        self.assertIn("tests\\test_cautious_live_widening_pilot_final_handoff_packet.py", paths)
        self.assertTrue(any(path.startswith("scripts\\run_patch_*") for path in paths))

    def test_rendered_section_treats_runtime_reports_as_noncanonical(self) -> None:
        section = render_post_275_repo_inventory_section()
        self.assertIn("external Desktop artifacts", section)
        self.assertIn("not repo-tracked source files", section)
        self.assertIn("Runtime/report artifacts", section)
        self.assertIn("can be evidence", section)

    def test_rendered_section_keeps_execution_as_center_of_gravity(self) -> None:
        section = render_post_275_repo_inventory_section()
        self.assertIn(IMPLEMENTATION_CENTER_OF_GRAVITY, section)
        self.assertIn("implementation center of gravity", section)
        self.assertIn("must not absorb deep canonical logic", section)

    def test_rendered_section_preserves_safety_boundary(self) -> None:
        section = render_post_275_repo_inventory_section()
        self.assertIn("does not authorize live trading", section)
        self.assertIn("submit orders", section)
        self.assertIn("call wallet signing code", section)
        self.assertIn("authorize unattended live trading", section)

    def test_inventory_file_contains_post_275_refresh(self) -> None:
        inventory = Path("trader_repo_inventory.md")
        self.assertTrue(inventory.exists(), "trader_repo_inventory.md should exist after patch apply")
        text = inventory.read_text(encoding="utf-8")
        result = validate_repo_inventory_text(text)
        self.assertTrue(result.ok, f"missing={result.missing_markers}; stale={result.stale_markers}")

    def test_validator_rejects_stale_frontier_claims(self) -> None:
        bad = render_post_275_repo_inventory_section() + "\nPatch 134 is the latest overall frontier.\n"
        result = validate_repo_inventory_text(bad)
        self.assertFalse(result.ok)
        self.assertIn("Patch 134 is the latest overall frontier", result.stale_markers)


if __name__ == "__main__":
    unittest.main()
