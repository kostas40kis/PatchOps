from __future__ import annotations

from pathlib import Path
import unittest

from trader.execution.post_275_test_matrix_refresh import (
    CURRENT_ACCEPTED_FRONTIER,
    CURRENT_FRONTIER_MODULE,
    FULL_RELEASE_TEST_COUNT,
    all_required_surfaces,
    iter_group_patch_ranges,
    render_post_275_test_matrix_section,
    replace_or_append_section,
    summarize_post_275_test_matrix,
    validate_post_275_test_matrix_text,
    validation_group_names,
)


class Post275TestMatrixRefreshTests(unittest.TestCase):
    def test_validation_groups_cover_patch_252_to_275_surface_families(self) -> None:
        self.assertEqual(CURRENT_ACCEPTED_FRONTIER, "Patch 275")
        self.assertEqual(CURRENT_FRONTIER_MODULE, "cautious_live_widening_pilot_final_handoff_packet.py")
        self.assertEqual(FULL_RELEASE_TEST_COUNT, 1774)

        ranges = iter_group_patch_ranges()
        self.assertIn("Patch 252-253", ranges)
        self.assertIn("Patch 254-260", ranges)
        self.assertIn("Patch 261-270", ranges)
        self.assertIn("Patch 271-275", ranges)

        names = "\n".join(validation_group_names())
        self.assertIn("Release gate and checkpoint evidence", names)
        self.assertIn("Pilot runbook and proposal controls", names)
        self.assertIn("Operator handoff", names)
        self.assertIn("Pilot suite", names)

        surfaces = all_required_surfaces()
        self.assertIn("tests.test_release_gate_script", surfaces)
        self.assertIn("tests.test_green_checkpoint_tag", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_runbook", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_go_no_go_summary", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_operator_handoff", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_recovery_drill", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_suite_runner", surfaces)
        self.assertIn("tests.test_cautious_live_widening_pilot_final_handoff_packet", surfaces)

    def test_rendered_section_contains_required_post_275_matrix_language(self) -> None:
        rendered = render_post_275_test_matrix_section()
        ok, issues = validate_post_275_test_matrix_text(rendered)
        self.assertTrue(ok, issues)
        self.assertEqual(issues, ())

        self.assertIn("Patch 252-275 validation surfaces", rendered)
        self.assertIn("release gate script contract tests", rendered)
        self.assertIn("green checkpoint tag tests", rendered)
        self.assertIn("pilot runbook tests", rendered)
        self.assertIn("pilot evidence/preflight/stop/monitor/review/go-no-go tests", rendered)
        self.assertIn(
            "operator handoff/acceptance/safety/readiness/execution-window/incident/recovery/audit/closeout/checklist tests",
            rendered,
        )
        self.assertIn("suite runner/documentation stop/release-readiness/milestone/final handoff tests", rendered)
        self.assertIn("full unittest discovery", rendered)
        self.assertIn("1774 tests OK", rendered)
        self.assertIn("does not authorize live trading", rendered)

    def test_validator_rejects_old_patch_134_only_frontier_story(self) -> None:
        stale_text = (
            "The current accepted frontier is Patch 134. "
            "The latest overall frontier is Patch 134. "
            "No Patch 275 validation surfaces are listed."
        )
        ok, issues = validate_post_275_test_matrix_text(stale_text)
        self.assertFalse(ok)
        self.assertTrue(any("Patch 252-275 validation surfaces" in issue for issue in issues))
        self.assertTrue(any("Patch 134" in issue for issue in issues))

    def test_replace_or_append_section_is_idempotent(self) -> None:
        base = "# Trader Test Matrix\n\nExisting content.\n"
        section = render_post_275_test_matrix_section()
        once = replace_or_append_section(base, section)
        twice = replace_or_append_section(once, section)
        self.assertEqual(once, twice)
        self.assertEqual(once.count("PATCH_278_POST_275_TEST_MATRIX_REFRESH_START"), 1)
        self.assertEqual(once.count("PATCH_278_POST_275_TEST_MATRIX_REFRESH_END"), 1)

    def test_summary_is_review_only_and_release_gate_centered(self) -> None:
        summary = summarize_post_275_test_matrix()
        self.assertIn("Patch 275", summary)
        self.assertIn("full unittest discovery", summary)
        self.assertIn("1774 tests OK", summary)
        self.assertIn("review-only", summary)

    def test_maintained_test_matrix_file_contains_patch_278_section_after_apply(self) -> None:
        matrix_path = Path(__file__).resolve().parents[1] / "trader_test_matrix.md"
        self.assertTrue(matrix_path.exists(), "trader_test_matrix.md should exist after patch apply")
        text = matrix_path.read_text(encoding="utf-8")
        ok, issues = validate_post_275_test_matrix_text(text)
        self.assertTrue(ok, issues)
        self.assertIn("PATCH_278_POST_275_TEST_MATRIX_REFRESH_START", text)
        self.assertIn("PATCH_278_POST_275_TEST_MATRIX_REFRESH_END", text)


if __name__ == "__main__":
    unittest.main()
