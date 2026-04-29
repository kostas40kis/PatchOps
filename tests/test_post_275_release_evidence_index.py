import unittest

from trader.execution.post_275_release_evidence_index import (
    ReleaseEvidenceEntry,
    build_default_post_275_release_evidence_index,
    build_release_evidence_index,
    index_to_dict,
    render_release_evidence_index,
    validate_release_entry,
)


class Post275ReleaseEvidenceIndexTests(unittest.TestCase):
    def test_default_entries_render_in_chronological_order(self):
        index = build_default_post_275_release_evidence_index()
        ranges = [entry.patch_range for entry in index.chronological_entries]
        self.assertEqual(ranges, ["252", "253", "254", "255R-260", "261-270", "271-275"])

    def test_patch_275_is_latest_accepted_entry(self):
        index = build_default_post_275_release_evidence_index()
        latest = index.latest_accepted_entry
        self.assertIsNotNone(latest)
        self.assertEqual(latest.patch_range, "271-275")
        self.assertEqual(index.current_frontier_patch, 275)
        self.assertEqual(latest.commit_sha, "4d24c9ec65a8f2643a6b1ba482e82a27915fb77b")
        self.assertEqual(latest.github_ci_run_id, "25049340880")
        self.assertEqual(latest.test_count, 1774)

    def test_incomplete_evidence_is_marked_incomplete(self):
        index = build_default_post_275_release_evidence_index()
        incomplete_ranges = [entry.patch_range for entry in index.incomplete_entries]
        self.assertIn("252", incomplete_ranges)
        self.assertIn("255R-260", incomplete_ranges)
        text = render_release_evidence_index(index)
        self.assertIn("Result: INCOMPLETE", text)
        self.assertIn("Commit SHA: MISSING", text)
        self.assertIn("GitHub CI run: MISSING", text)

    def test_pass_entry_without_remote_sha_or_ci_is_blocked(self):
        bad = ReleaseEvidenceEntry(
            patch_range="999",
            title="bad evidence",
            release_result="PASS",
            commit_sha="",
            github_ci_run_id="",
        )
        self.assertEqual(bad.effective_result, "BLOCKED_INCOMPLETE_EVIDENCE")
        issues = validate_release_entry(bad)
        self.assertIn("PASS entry missing remote commit SHA", issues)
        self.assertIn("PASS entry missing GitHub CI run ID", issues)

    def test_custom_index_keeps_only_complete_pass_entries_as_accepted(self):
        entries = [
            ReleaseEvidenceEntry(patch_range="10", title="complete", release_result="PASS", commit_sha="abc", github_ci_run_id="123"),
            ReleaseEvidenceEntry(patch_range="11", title="missing ci", release_result="PASS", commit_sha="abc", github_ci_run_id=""),
            ReleaseEvidenceEntry(patch_range="12", title="incomplete", release_result="INCOMPLETE"),
        ]
        index = build_release_evidence_index(entries)
        self.assertEqual([entry.patch_range for entry in index.accepted_entries], ["10"])
        self.assertEqual(index.latest_accepted_entry.patch_range, "10")

    def test_rendered_index_is_review_only_and_not_live_authorization(self):
        text = render_release_evidence_index()
        self.assertIn("POST-275 RELEASE EVIDENCE INDEX", text)
        self.assertIn("Current accepted frontier: Patch 275", text)
        self.assertIn("does not authorize live trading", text)
        self.assertIn("Final handoff is not an execution bridge", text)
        self.assertNotIn("authorizes live trading", text.lower().replace("does not authorize live trading", ""))

    def test_index_to_dict_contains_current_frontier_and_effective_results(self):
        payload = index_to_dict()
        self.assertEqual(payload["current_frontier_patch"], 275)
        self.assertEqual(payload["latest_accepted_patch_range"], "271-275")
        results = {entry["patch_range"]: entry["effective_result"] for entry in payload["entries"]}
        self.assertEqual(results["271-275"], "PASS")
        self.assertEqual(results["252"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
