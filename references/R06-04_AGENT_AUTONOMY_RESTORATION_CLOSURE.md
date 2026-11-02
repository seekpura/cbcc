# R06-04 Agent Autonomy Restoration — Closure Authority

## Scope

R06-04 restores Agent/caller authority where an explicitly authored empty collection (`[]`) is a real decision and must not be reinterpreted as “missing; synthesize a Runtime default”.

This task does **not** remove deterministic Product Truth, compliance, platform, schema, hash, security, or Provider/Review lineage constraints. Runtime compatibility synthesis remains allowed only when the relevant Agent/caller field is absent.

## Locked presence semantics

| Decision surface | Explicit empty | Missing field |
| --- | --- | --- |
| research requirements | preserve zero; no synthetic research actions | decision-gap fallback allowed |
| research stop conditions | preserve zero | compatibility defaults allowed |
| content families | preserve zero | task-scope derivation allowed |
| creative opportunities | preserve authored zero universe | opportunity synthesis allowed |
| creative directions | preserve zero; do not auto-select | compatibility synthesis allowed |
| asset jobs | preserve zero assets | decision-derived auto-curation allowed |
| video jobs | preserve zero dynamic jobs | content/asset-derived fallback allowed |
| paid campaigns | preserve zero campaigns | paid-asset/content-derived fallback allowed |

## Hard-boundary invariant

Agent autonomy is subordinate to deterministic truth/risk boundaries. In particular:

- Product Truth unknown/evidence state is not changed by an empty research plan.
- PlatformCompiler and compliance/claim gates may still HOLD a requested deliverable when a hard rule is unresolved.
- `iteration_policy.stop` cannot override current-scope blocking frontier items.
- Provider Result → Review → Revision hashes/provenance remain deterministic.

## Creative and asset invariant

When assets exist but the Agent explicitly authors no creative direction, Runtime must not silently select one. The next-action frontier exposes `AUTHOR_OR_SELECT_CREATIVE_DIRECTION` when that decision is required for the current scope.

When the Agent/caller explicitly authors zero asset/video/paid jobs, Runtime does not manufacture those objects merely to satisfy a family/surface convention. If the requested scope truly requires them, readiness/frontier mechanisms report the unresolved decision instead of inventing it.

## Compatibility invariant

Missing fields continue to support mature compatibility behavior. R06-04 therefore restores authority without deleting the established fallbacks used by older callers that do not provide Agent-authored plans.

## Anti-regression test

`tests/test_v0682_r0604_agent_autonomy_restoration.py`

The test distinguishes **explicit empty** from **absent** for each locked surface above.

## Non-claims / later tasks

- R06-05 professional capability completeness is not part of this task.
- R06-07 remains responsible for broader real external Provider actual-media E2E.
- R06-10 remains responsible for historical stale workflow/test debris cleanup.
