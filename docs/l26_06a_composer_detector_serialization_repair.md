# L26.6A Composer Detector Serialization Repair

L26.6 failed in the target project validation command because the composer detector serialized candidates, rebuilt `ComposerDetectorResult` from that serialized payload, and then called `dataclasses.asdict()` on candidate dictionaries.

This repair keeps the same browser behavior boundary and fixes only the serialization/reporting layer:

- `to_payload()` now accepts both dataclass candidates and dictionary candidates;
- candidate round-trips are covered by a regression test;
- the live composer detector reruns against the real targeted ChatGPT page;
- no prompt text is entered;
- no page controls are clicked;
- no prompt is submitted;
- no downloads or run-package actions occur.

L26.6A acceptance proves the composer diagnostic scan completes and emits JSON/report evidence without reintroducing the dataclass/dict serialization crash.
