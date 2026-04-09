# Bundle release readiness

This document explains how the maintained bundle surfaces now participate in `release-readiness`.

The release gate is no longer only about classic manifest-era surfaces. It must also confirm that the maintained bundle docs, bundle workflows, and bundle tests are still present.

## Required bundle release docs

- `docs/bundle_contract_packet.md`
- `docs/bundle_regression_gate.md`
- `docs/bundle_smoke_gate.md`
- `docs/self_hosted_bundle_proof.md`
- `docs/bundle_release_readiness.md`

## Required bundle release workflows

- `patchops/bundles/authoring.py`
- `patchops/bundles/launcher_emitter.py`

## Required bundle release tests

- `tests/test_bundle_contract_packet_current.py`
- `tests/test_bundle_manifest_regression_gate_current.py`
- `tests/test_bundle_post_build_smoke_gate_current.py`
- `tests/test_self_hosted_bundle_authoring_proof_current.py`

## Operator meaning

A release-ready wrapper now needs both worlds to stay intact:

- the classic manifest review surfaces
- the maintained bundle review, build, and post-build smoke surfaces

Continue patch by patch from evidence.
