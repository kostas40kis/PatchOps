from pathlib import Path
import unittest

from trader.execution.post_275_patch_ledger_refresh import (
    CLEANUP_MILESTONE_PATCH,
    CURRENT_FRONTIER_CI_RUN,
    CURRENT_FRONTIER_COMMIT,
    CURRENT_FRONTIER_FULL_TESTS,
    CURRENT_FRONTIER_MODULE,
    CURRENT_FRONTIER_PATCH,
    PRODUCTION_MILESTONE_PATCH,
    build_post_275_runway_segments,
    render_post_275_ledger_section,
    render_validation_summary,
    replace_or_append_ledger_section,
    validate_patch_ledger_text,
)


class Post275PatchLedgerRefreshTests(unittest.TestCase):
    def test_current_frontier_constants_match_accepted_patch_275_evidence(self):
        self.assertEqual(CURRENT_FRONTIER_PATCH, 275)
        self.assertEqual(CURRENT_FRONTIER_MODULE, "cautious_live_widening_pilot_final_handoff_packet.py")
        self.assertEqual(CURRENT_FRONTIER_COMMIT, "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b")
        self.assertEqual(CURRENT_FRONTIER_CI_RUN, "25049340880")
        self.assertEqual(CURRENT_FRONTIER_FULL_TESTS, "1774 tests OK")
        self.assertEqual(PRODUCTION_MILESTONE_PATCH, 125)
        self.assertEqual(CLEANUP_MILESTONE_PATCH, 134)

    def test_runway_segments_cover_required_patch_batches(self):
        segments = build_post_275_runway_segments()
        ranges = [segment.patch_range for segment in segments]
        self.assertEqual(
            ranges,
            ["Patch 252", "Patch 253", "Patch 254", "Patch 255R-260", "Patch 261-270", "Patch 271-275"],
        )
        self.assertTrue(all(segment.status for segment in segments))
        self.assertTrue(all("no" in segment.safety_summary.lower() or "not" in segment.safety_summary.lower() for segment in segments))

    def test_rendered_section_contains_frontier_and_release_evidence_batches(self):
        section = render_post_275_ledger_section()
        status = validate_patch_ledger_text(section)
        self.assertTrue(status.is_ready, render_validation_summary(status))
        self.assertIn("latest overall accepted frontier", section)
        self.assertIn("Patch 275", section)
        self.assertIn("release evidence batches", section)
        self.assertIn("Patch 125 remains the production milestone", section)
        self.assertIn("Patch 134 remains the cleanup/documentation milestone", section)
        self.assertIn("Patch 134 is not the latest overall frontier", section)
        self.assertIn("does not authorize live trading", section)

    def test_replace_or_append_section_is_idempotent(self):
        original = "# Trader Patch Ledger\n\nOld content.\n"
        once = replace_or_append_ledger_section(original)
        twice = replace_or_append_ledger_section(once)
        self.assertEqual(once, twice)
        self.assertEqual(once.count("PATCH_277_POST_275_PATCH_LEDGER_REFRESH_START"), 1)
        self.assertEqual(once.count("PATCH_277_POST_275_PATCH_LEDGER_REFRESH_END"), 1)

    def test_validator_rejects_patch_134_as_latest_overall_frontier(self):
        bad = render_post_275_ledger_section() + "\nPatch 134 is the latest overall frontier.\n"
        status = validate_patch_ledger_text(bad)
        self.assertFalse(status.is_ready)
        self.assertIn("removal of Patch 134 latest-overall-frontier claim", status.missing_requirements)

    def test_validator_accepts_plain_or_markdown_patch_134_reclassification(self):
        plain = render_post_275_ledger_section()
        markdown = plain.replace("Patch 134 is not the latest overall frontier", "Patch 134 is **not** the latest overall frontier")
        self.assertTrue(validate_patch_ledger_text(plain).is_ready)
        self.assertTrue(validate_patch_ledger_text(markdown).is_ready)

    def test_repo_ledger_contains_patch_277_refresh_after_apply(self):
        ledger = Path("trader_patch_ledger.md")
        self.assertTrue(ledger.exists(), "trader_patch_ledger.md should exist after Patch 277 apply")
        text = ledger.read_text(encoding="utf-8")
        status = validate_patch_ledger_text(text)
        self.assertTrue(status.is_ready, render_validation_summary(status))
        self.assertIn("Patch 271-275", text)
        self.assertIn("final handoff", text.lower())
        self.assertNotIn("Patch 134 is the latest overall frontier", text)
        self.assertNotIn("latest overall accepted frontier is Patch 134", text)


if __name__ == "__main__":
    unittest.main()
