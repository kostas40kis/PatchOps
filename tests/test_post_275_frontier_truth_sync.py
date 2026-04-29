import unittest

from src.trader.execution.post_275_frontier_truth_sync import (
    CLEANUP_DOCUMENTATION_FRONTIER,
    CURRENT_FRONTIER_PREFIX,
    POST_275_FRONTIER,
    PRODUCTION_MILESTONE_FRONTIER,
    classify_frontier_signal,
    classify_frontier_signals,
    current_frontier,
    export_wording_is_stale,
    render_post_275_frontier_payload,
    render_post_275_frontier_summary,
    validate_post_275_payload,
)


class Post275FrontierTruthSyncTests(unittest.TestCase):
    def test_patch_275_is_current_accepted_frontier(self) -> None:
        frontier = current_frontier()
        self.assertEqual(frontier.patch_number, 275)
        self.assertEqual(frontier.module_name, "cautious_live_widening_pilot_final_handoff_packet.py")
        self.assertEqual(frontier.commit_sha, "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b")
        self.assertEqual(frontier.ci_run_id, "25049340880")
        self.assertEqual(frontier.ci_result, "success")
        self.assertEqual(frontier.release_result, "PASS")
        self.assertEqual(frontier.full_test_result, "1774 tests OK")
        self.assertEqual(frontier.frontier_kind, "latest_accepted_frontier")

    def test_patch_70_presence_markers_are_historical_only(self) -> None:
        markers = classify_frontier_signals(
            [
                "entry_execution_coordinator.md present : True",
                "run_patch_70_entry_execution_coordinator present : True",
                70,
            ]
        )
        self.assertTrue(markers)
        self.assertTrue(all(item["is_current_frontier"] is False for item in markers))
        self.assertTrue(all("historical" in str(item["classification"]) for item in markers))

    def test_patch_125_and_patch_134_remain_milestones_not_latest_frontier(self) -> None:
        patch_125 = classify_frontier_signal("Patch 125 cautious_live_manual_review_request.py")
        patch_134 = classify_frontier_signal("Patch 134 repo_backup_archive_cleanup.py")
        self.assertEqual(patch_125["classification"], "production_milestone_frontier")
        self.assertFalse(patch_125["is_current_frontier"])
        self.assertEqual(patch_134["classification"], "cleanup_documentation_frontier")
        self.assertFalse(patch_134["is_current_frontier"])
        self.assertEqual(PRODUCTION_MILESTONE_FRONTIER.patch_number, 125)
        self.assertEqual(CLEANUP_DOCUMENTATION_FRONTIER.patch_number, 134)

    def test_export_summary_uses_accepted_release_evidence_not_presence_signal_wording(self) -> None:
        summary = render_post_275_frontier_summary(
            [
                "entry_execution_coordinator.md present : True",
                "run_patch_70_entry_execution_coordinator present : True",
            ]
        )
        self.assertIn(CURRENT_FRONTIER_PREFIX, summary)
        self.assertIn("Patch number: 275", summary)
        self.assertIn("Patch module: cautious_live_widening_pilot_final_handoff_packet.py", summary)
        self.assertIn("Release result: PASS", summary)
        self.assertIn("Historical/context signal", summary)
        self.assertNotIn("Current frontier signals detected in this export", summary)

    def test_stale_export_wording_is_detected(self) -> None:
        stale_export = """
Current frontier signals detected in this export:
entry_execution_coordinator.md present : True
run_patch_70_entry_execution_coordinator present : True
"""
        self.assertTrue(export_wording_is_stale(stale_export))
        fixed_export = render_post_275_frontier_summary([])
        self.assertFalse(export_wording_is_stale(fixed_export))

    def test_payload_is_structured_and_validates(self) -> None:
        payload = render_post_275_frontier_payload(["run_patch_70_entry_execution_coordinator present : True"])
        self.assertEqual(payload["current_frontier"], POST_275_FRONTIER.as_dict())
        self.assertEqual(validate_post_275_payload(payload), [])
        self.assertTrue(payload["safety"]["review_only"])
        self.assertTrue(payload["safety"]["no_live_behavior_widening"])
        self.assertFalse(payload["safety"]["submits_orders"])
        self.assertFalse(payload["safety"]["touches_wallets"])

    def test_invalid_payload_fails_closed(self) -> None:
        payload = render_post_275_frontier_payload([])
        payload["current_frontier"] = dict(payload["current_frontier"])
        payload["current_frontier"]["patch_number"] = 134
        payload["current_frontier"]["release_result"] = "UNKNOWN"
        issues = validate_post_275_payload(payload)
        self.assertIn("patch_275_not_current_frontier", issues)
        self.assertIn("release_result_not_pass", issues)


if __name__ == "__main__":
    unittest.main()
