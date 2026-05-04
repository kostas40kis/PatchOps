# L26.12S Post-Submit Idle Observer

L26.12R accepted the real browser upload+submit milestone. The next step is not to click downloads yet; it is to know when the submitted chat appears idle enough for a later artifact-detection probe.

L26.12S:

1. reuses L26.12R upload+submit;
2. observes Edge through UIA only;
3. records control counts and generic stop/send-like state;
4. does not read or log conversation text;
5. does not click generated files or downloads;
6. reports `ready_for_next_probe` when Edge is present and no stop-generating control is observed at the end.

This is the bridge between submit and future downloadable artifact detection.
