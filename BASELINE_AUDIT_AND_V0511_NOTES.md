# CBCC v0.5.11 — Baseline Audit and Integration Notes

## Baseline authority
The only source baseline for this release is the user-supplied:

`cross-border-commerce-creative-v0.5.10-evidence-commerce-reconciliation-depth.zip`

Older versions remain historical construction nodes only.

## Path-level non-regression
Compared directly against the uploaded v0.5.10 ZIP:

- v0.5.10 baseline files: **427**
- v0.5.11 final files: **436**
- baseline paths preserved: **427 / 427**
- missing baseline paths: **0**
- additive paths: **9**

Added paths:

1. `BASELINE_AUDIT_AND_V0511_NOTES.md`
2. `CHANGELOG_V0511.md`
3. `INTEGRATION_AUDIT_V0511.md`
4. `INTEGRATION_QUALITY_VALIDATION_V0511.md`
5. `knowledge/evidence_quality_weighted_reconciliation.md`
6. `knowledge/strategy_revision_integration.md`
7. `prompts/evidence_quality_weighted_reconciliation.md`
8. `prompts/strategy_revision_integration.md`
9. `tests/test_v0511_integration_quality_depth.py`

No existing source path was removed to add the new integration logic.

## What v0.5.11 actually fixes
This release is not a Gate/test-count release. It closes wiring gaps found by tracing the compiler and final artifacts:

1. **Evidence quality actually weights strategy reconciliation.** Freshness, traceability, representativeness metadata, scope match, explicit source quality and source agreement/conflict now affect evidence pressure.
2. **Market evidence has a safe route to Dynamic Assets.** Search/Review/Competitor observations become Product-Truth-Fit review candidates; only explicit fit confirmation can create a `MARKET_THEME_FIT` asset.
3. **Ads / Feedback route back into strategy.** Diagnostics now produce local `StrategyRevisionRoute` records with edit/freeze layers and enter Strategy §9 / decision traces.
4. **Capability wiring is inspectable.** `capability_integration_map.json` distinguishes active wiring, inactive-no-input wiring, and actual integration gaps.
5. **Knowledge Authority traces are stable.** Five historical strategy-depth knowledge documents now have explicit IDs instead of falling back to path/null identity.
6. **Legacy calculator double-truth is removed.** Root calculator CLIs remain available but delegate to canonical Runtime engines.
7. **Delivery exposes the integration artifacts.** Market Fit, Revision Routing and Capability Integration Map are included in supporting analysis.

## Validation meaning
The full regression suite is used only for compatibility/non-regression. It is not evidence that the professional system is complete.

The meaningful v0.5.11 integration validation is the dataflow change:

- same review signal + weak/stale/wrong-scope evidence → weighted evidence 6.0; Category prior remains first;
- same review signal + strong/current/scope-matched evidence → weighted evidence 108.0; current evidence can reorder strategy;
- Market-fit candidate before explicit Product Truth confirmation → no asset;
- one explicit fit confirmation → one market-driven asset;
- Ads + Feedback → local revision routes rather than whole-plan rewrite;
- Provider jobs are materialized from frozen packages but external execution remains unauthorized until an explicit Provider result is returned.

## Preserved contracts
- all nine Strategy Authority sections;
- dynamic rather than fixed asset count;
- complete per-asset `00–11` package;
- Provider Job → Result → Review Item → Local Revision → Package Hash contracts;
- Final Copy version/review boundary;
- Knowledge/Ontology/Prompt runtime selection;
- category-prior/evidence authority order;
- platform verification boundary without strategic surface censorship.

See `INTEGRATION_AUDIT_V0511.md`, `INTEGRATION_QUALITY_VALIDATION_V0511.md`, `CHANGELOG_V0511.md`, and `CURRENT_HANDOFF.md`.
