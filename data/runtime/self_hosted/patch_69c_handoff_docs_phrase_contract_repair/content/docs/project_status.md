# PatchOps project status

## Current state snapshot

This document distinguishes stable now from future work.

PatchOps now spans two truths at once:

- the original buildout circle is stable enough to treat as a maintained wrapper utility
- the handoff-first Stage 2 UX buildout has now been completed through Patch 69

This also preserves the older late Stage 1 / pre-Stage 2 consolidation language that existing repo tests still expect.

## Stable now

The items below exist in the repo today and should be treated as shipped behavior.

### Core wrapper behavior that exists in the repo today

Stable now, PatchOps owns:

- manifest-driven apply flow
- verify-only flow
- explicit profile resolution
- deterministic backup and write behavior
- canonical single-report evidence
- failure classification
- verification-only reruns
- wrapper-only retry classification support
- thin launcher surfaces
- example and schema authoring surfaces

Concrete maintained operator surfaces include:

- `patchops.cli examples`
- `patchops.cli profiles`
- `patchops.cli schema`
- `patchops.cli template`
- `powershell/Invoke-PatchManifest.ps1`
- `powershell/Invoke-PatchVerify.ps1`

### Stable now: handoff-first continuation surfaces

The handoff-first UX is now also part of shipped behavior.

Stable handoff surfaces now include:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`
- `py -m patchops.cli export-handoff`
- `powershell/Invoke-PatchHandoff.ps1`

### Stable now: milestone references that still matter

Important historical anchors that remain part of the maintained story:

- Patch 41 hardened the `generic_python_powershell` profile surface.
- Patch 48 provided the final initial milestone gate.

Those earlier anchors still matter because the repo should preserve continuity with the already-tested wrapper baseline.

## What the operator can do now

The operator can now change LLMs like this:

1. run one export command
2. upload one handoff bundle
3. paste one generated prompt
4. the new LLM continues from the current state

That is the practical meaning of seamless transition.

## Future work, not yet shipped behavior

This section explains what remains future work rather than current behavior.

Future work, not yet shipped behavior, would be things like:

- richer handoff packaging beyond the current bundle
- more profiles and profile-specific ergonomics
- broader fixture repos and deeper integration suites
- additional launcher conveniences
- further maintenance-mode polish after the handoff-first stop

## What remains future work rather than current behavior

Do not confuse “could be improved later” with “not implemented.”

What remains future work rather than current behavior should build on the current handoff-first base rather than replace it casually.

## Current continuation flow

For continuation today:

1. generate handoff with:
   - `py -m patchops.cli export-handoff --report-path <path>`
   - or `.\powershell\Invoke-PatchHandoff.ps1 -SourceReportPath <path>`
2. upload the generated bundle from `handoff/bundle/current`
3. paste `handoff/next_prompt.txt`
4. let the next LLM continue with the exact next action

## Summary

PatchOps now has both:

- a stable wrapper baseline
- and a real handoff-first continuation loop

Future onboarding should now start from the handoff artifact, not from scattered docs.